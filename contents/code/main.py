# -*- coding: utf-8 -*-
# copyright 2009  Nik Lutz nik.lutz@gmail.com
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
# USA
###

###
# Veromix  - A Pulseaudio volume control
#
# Veromix has two components:
# - a service that sends notifications over dbus and offers an interface
#   to perform actions (set volume, mute ...)
# - the plasmoid that connects to the service
#
# The service is launchd by dbus. For this to work veromix installs a service
# description-file in /usr/share/dbus-1/services/ called org.veromix.pulseaudio.service .
#
# Whithout this separation there where two two problems:
# - one could only add one veromix-plasmoid to the desktop/panel/.. (CTypes binds the
#   loaded module to the parent process and accepts only one callback-function)
# - There was crash that could not be fixed: When the parent process (plasma, plasmoidviewer, ..) exits
#   the embedded python crashed. I don't know if this is a python or kde bug. Nobody could help me.
#
# Pulseaudio should provide their own dbus-interface. But currently they are still planning it:
# http://pulseaudio.org/wiki/DBusInterface
#
# The python-interface to pulseaudio is a mix of these two projects:
# https://launchpad.net/earcandy
# https://fedorahosted.org/pulsecaster/
# Thank you guys!
###### December 2009 & July 2010


import commands

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import uic
from PyKDE4 import plasmascript
from PyKDE4.plasma import Plasma
from PyKDE4.kdeui import KIcon
from PyKDE4.kdeui import KActionCollection
from PyKDE4.kdeui import KShortcut
from PyKDE4.kdecore import *

from VeroMix import VeroMix
from Utils import *

class VeroMixPlasmoid(plasmascript.Applet):
    VERSION="0.9.0"
    
    nowplaying_player_added = pyqtSignal(QString, QObject)
    nowplaying_player_removed = pyqtSignal(QString )
    nowplaying_player_dataUpdated = pyqtSignal(QString, dict)

    def __init__(self,parent,args=None):        
        plasmascript.Applet.__init__(self,parent)
        self.engine = None

    def init(self):
        out = commands.getstatusoutput("xdg-icon-resource install --size 128 " + unicode(self.package().path()) + "contents/icons/veromix-plasmoid-128.png veromix-plasmoid")
        if out[0] == 0:
            print "veromix icon installed"
            #gc.writeEntry("gmail-plasmoid-128.png", vers["gmail-plasmoid-128.png"])
        else:
            print "Error installing veromix icon:", out

        createDbusServiceDescription(self)
	
        KGlobal.locale().insertCatalog("veromix-plasmoid")

        self.setHasConfigurationInterface(True)
        self.setAspectRatioMode(Plasma.IgnoreAspectRatio)
        self.theme = Plasma.Svg(self)

        self.widget = VeroMix(self)
        self.widget.init()
        if self.isNowplayingEnabled():
            self.initNowPlaying()

        defaultSize =  QVariant(QSize (0,0))
        size = self.config().readEntry("size", defaultSize ).toSize()
        if (size != defaultSize) :
            self.widget.setPreferredSize(size.width(), size.height())
        else:
            self.widget.setPreferredSize(400 ,145)

        self.connect(self.widget, SIGNAL("resized()"), self.dialogResized)
        try:
            self.setGraphicsWidget(self.widget)
            self.applet.setPassivePopup(True)
            ## FIXME: see fixPopupcion
            self.setPopupIcon(KIcon("audio-volume-high"))
            #self.setPopupIcon("audio-volume-muted")
            # dont know why but adding it a second time helps (otherwise it
            # wont popup when you add it directly to the panel)
            self.setGraphicsWidget(self.widget)
            self.connect(self.applet, SIGNAL("appletDestroyed(Plasma::Applet*)"), self.doExit)
            self.setBackgroundHints(Plasma.Applet.NoBackground)
            self.applyConfig()
        except AttributeError , e:
            print e
            updateMetadataDesktop(self)      
            
        self.initTooltip()
        self.initShortcuts()
        QTimer.singleShot(1000, self.fixPopupIcon)

    def initShortcuts(self):
        self.actionCollection = KActionCollection(self)
        
        louder = self.actionCollection.addAction("VeromixVolumeUp")
        louder.setText( i18n("Veromix volume up") )
        #louder.setGlobalShortcut(KShortcut(Qt.CTRL + Qt.ALT+ Qt.Key_U))
        louder.setGlobalShortcut(KShortcut())        
        louder.triggered.connect(self.widget.on_step_volume_up)
        
        lower = self.actionCollection.addAction("VeromixVolumeDown")
        lower.setText(i18n("Veromix volume down"))
        #lower.setGlobalShortcut(KShortcut(Qt.CTRL + Qt.ALT+ Qt.Key_D))
        lower.setGlobalShortcut(KShortcut())        
        lower.triggered.connect(self.widget.on_step_volume_down)
        
        mute = self.actionCollection.addAction("VeromixVolumeMute")
        mute.setText(i18n("Veromix toggle  mute"))
        #lower.setGlobalShortcut(KShortcut(Qt.CTRL + Qt.ALT+ Qt.Key_M))
        mute.setGlobalShortcut(KShortcut())        
        mute.triggered.connect(self.widget.on_toggle_mute)        


    def initTooltip(self):
        if (self.formFactor() != Plasma.Planar):   
            self.tooltip = Plasma.ToolTipContent() 
            self.tooltip.setImage(pixmapFromSVG("audio-volume-high"))
            self.tooltip.setMainText(i18n( "Main Volume") )
            #self.tooltip.setSubText( "" )    
            Plasma.ToolTipManager.self().setContent(self.applet, self.tooltip)
            Plasma.ToolTipManager.self().registerWidget(self.applet)

    def updateIcon(self):
        icon_state = "audio-volume-muted"
        vol = self.widget.getDefaultSink().getVolume()
        if self.widget.getDefaultSink().isMuted() :
            icon_state= "audio-volume-muted"
        else:
            if  vol == 0:
                icon_state = "audio-volume-muted"
            elif vol < 30: 
                icon_state= "audio-volume-low"
            elif vol < 70:   
                icon_state= "audio-volume-medium"
            else:
                icon_state= "audio-volume-high"
        self.setPopupIcon(icon_state)
        if (self.formFactor() != Plasma.Planar):                  
            self.tooltip.setImage(pixmapFromSVG(icon_state))
            ## FIXME this should better go to toolTipAboutToShow but is not working:
            # https://bugs.kde.org/show_bug.cgi?id=254764                   
            self.tooltip.setMainText( self.widget.getDefaultSink().app)
            self.tooltip.setSubText( str(vol) + "%")
            Plasma.ToolTipManager.self().setContent(self.applet, self.tooltip)
     
    def showTooltip(self):
        Plasma.ToolTipManager.self().show(self.applet)
        
    @pyqtSlot(name="toolTipAboutToShow")
    def toolTipAboutToShow(self):
        pass 
        
    ## FIXME Looks like a bug in plasma: Only when sending a
    # KIcon instance PopUpApplet acts like a Poppupapplet...
    def fixPopupIcon(self):
        self.widget.getDefaultSink().updateIcon() 

    def doExit(self):
        # prevent crash in plasmoidviewer
        self.widget.doExit()
        self.widget.deleteLater()

    def dialogResized(self):
        if self.isPopupShowing():
            self.config().writeEntry("size", QVariant(self.widget.size()))

    def query_application(self, query):
        #print "query: ", query
        if not query :
            return None
        needle = query.lower()
        if self.engine == None:
            self.engine = self.dataEngine("apps")
        for source in self.engine.sources():
            key = unicode(source).replace(".desktop", "")
            if  ( 0<=  key.find(needle) ) or  (0 <= needle.find(key) )  :
                #print "found: ",key,  needle , source
                result = self.engine.query(source)
                if QString("iconName") in result:
                    iconname = result[QString("iconName")].toString()
                    return iconname
        return None

    def wheelEvent(self, event):
        self.widget.on_step_volume( (event.delta() > 0) )

    def mousePressEvent(self, event):
        if event.button() == Qt.MidButton:
            self.widget.on_toggle_mute()

    def createConfigurationInterface(self, parent):        
        self.config_widget = QWidget(parent)
        self.connect(self.config_widget, SIGNAL('destroyed(QObject*)'), self.configWidgetDestroyed)
        
        self.config_ui = uic.loadUi(str(self.package().filePath('ui', 'appearance.ui')), self.config_widget)        
        self.config_ui.showBackground.setCurrentIndex( self.config().readEntry("background",False).toInt() [0] ) 
        self.config_ui.popupMode.setCurrentIndex( self.config().readEntry("popupMode",False).toInt() [0])
        self.config_ui.useTabs.setChecked(self.useTabs() )
        self.config_ui.version.setText(VeroMixPlasmoid.VERSION)
        parent.addPage(self.config_widget, i18n("Appearance"), "veromix-plasmoid-128" )
       
        self.nowplaying_widget = QWidget(parent)
        self.nowplaying_ui = uic.loadUi(str(self.package().filePath('ui', 'nowplaying.ui')), self.nowplaying_widget)    
        
        self.nowplaying_ui.mediaplayerBlacklist.setPlainText(self.getNowplayingPlayerBlacklistString() ) 
        self.nowplaying_ui.mpris2List.setPlainText(self.getMpris2ClientsString()) 
        self.nowplaying_ui.runningMediaplayers.setPlainText(self.getNowplayingSourcesString()) 
        self.nowplaying_ui.runningMediaplayers.setReadOnly(True) 
        
        self.nowplaying_ui.useNowplaying.setChecked(self.isNowplayingEnabled() ) 
        self.nowplaying_ui.useNowplaying.stateChanged.connect(self.on_setting_nowplaying_changed)        
        parent.addPage(self.nowplaying_widget, i18n("Media Player Controls"), "veromix-plasmoid-128" )      
        
        #self.about_widget = QWidget(parent)
        #self.about_ui = uic.loadUi(str(self.package().filePath('ui', 'about.ui')), self.about_widget)
        #self.about_ui.version.setText(VeroMixPlasmoid.VERSION)
        #parent.addPage(self.about_widget, "About", "help-about" )
        return self.config_widget

    def configChanged(self):
        self.config().writeEntry("background",str(self.config_ui.showBackground.currentIndex()))
        self.config().writeEntry("popupMode", str(self.config_ui.popupMode.currentIndex()))        
        self.config().writeEntry("useTabs", bool(self.config_ui.useTabs.isChecked()))        
        
        self.config().writeEntry("useNowplaying", str(self.nowplaying_ui.useNowplaying.isChecked()))                
        self.config().writeEntry("mpris2List",str(self.nowplaying_ui.mpris2List.toPlainText()).strip() )
        self.config().writeEntry("nowplayingBlacklist",str(self.nowplaying_ui.mediaplayerBlacklist.toPlainText()).strip())
        self.applyConfig()

    def on_setting_nowplaying_changed(self, value):
        aBoolean = (value == 2)
        self.nowplaying_ui.mediaplayerBlacklist.setEnabled(aBoolean)
        self.nowplaying_ui.mediaplayerBlacklistLabel.setEnabled(aBoolean)
        self.nowplaying_ui.mpris2List.setEnabled(aBoolean)
        self.nowplaying_ui.mpris2Label.setEnabled(aBoolean)
        self.nowplaying_ui.runningMediaplayers.setEnabled(aBoolean)
        self.nowplaying_ui.runningMediaplayersLabel.setEnabled(aBoolean)
        self.applyNowPlaying(aBoolean)
        self.nowplaying_ui.runningMediaplayers.setPlainText(self.getNowplayingSourcesString()) 
        
    def applyNowPlaying(self, enabled):            
        self.disableNowPlaying()     
        if enabled:
            self.initNowPlaying()         
            
    def applyConfig(self):
        self.applyNowPlaying(self.isNowplayingEnabled() )
                
        bg = self.config().readEntry("background",False).toBool()
        if  bg == 0:
            self.setBackgroundHints(Plasma.Applet.NoBackground)
        elif bg == 1:
            self.setBackgroundHints(Plasma.Applet.TranslucentBackground)
        else:
            self.setBackgroundHints(Plasma.Applet.StandardBackground)
            
        mode =  self.config().readEntry("popupMode",False).toInt()[0]
        if  mode== 0:
            self.setPassivePopup(False)
        elif mode == 1:
            self.setPassivePopup(True)
        else:
            self.setPassivePopup(True)
        self.update()           

    def configWidgetDestroyed(self):
        self.config_widget = None
        self.config_ui = None

    def useTabs(self):        
        return self.config().readEntry("useTabs",False ).toBool()    

### now playing

    def isNowplayingEnabled(self):
        return self.config().readEntry("useNowplaying",True).toBool() 

    def disableNowPlaying(self):        
        for player in self.widget.getNowPlaying():
            self.playerRemoved(player.controller.destination())

    def initNowPlaying(self):        
        self.now_playing_engine = self.dataEngine('nowplaying')
        self.connect(self.now_playing_engine, SIGNAL('sourceAdded(QString)'), self.playerAdded)
        self.connect(self.now_playing_engine, SIGNAL('sourceRemoved(QString)'), self.playerRemoved)
        self.connectToNowPlayingEngine()
            
    def connectToNowPlayingEngine(self):
        # get sources and connect
        for source in self.now_playing_engine.sources():
            self.playerAdded(source)
            
    def playerAdded(self, player):
        if not self.isNowplayingEnabled() :
            return 
        self.now_playing_engine.disconnectSource(player, self)
        for entry in self.getNowplayingPlayerBlacklist(): 
            if str(player).find(entry) == 0:
                return 
        self.now_playing_engine.connectSource(player, self, 2000)   
        controller = self.now_playing_engine.serviceForSource(player)
        self.nowplaying_player_added.emit(player, controller )

    def playerRemoved(self, player):
        self.now_playing_engine.disconnectSource(player, self)
        self.nowplaying_player_removed.emit(player)

    def getNowplayingSourcesString(self):
        val = ""
        for source in self.now_playing_engine.sources():
            val += source + "\n"
        return val
        
    def getNowplayingPlayerBlacklist(self):
        return self.getNowplayingPlayerBlacklistString().split("\n")
    
    def getNowplayingPlayerBlacklistString(self):
        default =  "org.mpris.MediaPlayer2.amarok\norg.mpris.bangarang"
        return self.config().readEntry("nowplayingBlacklist",default ).toString()    

    def getMpris2Clients(self):
        return self.getMpris2ClientsString().split("\n")
        
    def getMpris2ClientsString(self):        
        default = "org.mpris.MediaPlayer2.banshee"
        return self.config().readEntry("mpris2List",default ).toString()    

    @pyqtSignature('dataUpdated(const QString&, const Plasma::DataEngine::Data&)')
    def dataUpdated(self, sourceName, data):
        self.nowplaying_player_dataUpdated.emit(sourceName, data)


def CreateApplet(parent):
    # Veromix is dedicated to my girlfriend Vero.
    return VeroMixPlasmoid(parent)

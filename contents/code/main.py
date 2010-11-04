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


import sys, os, commands, time
from xdg import BaseDirectory

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyKDE4.plasma import Plasma
from PyKDE4 import plasmascript
from PyKDE4.kdeui import *
from PyKDE4.kdecore import *
from PyKDE4.kdecore import *
from PyKDE4.plasma import * 

import signal, os, datetime

from VeroMix import *
from SinkUI import *
from SinkInputUI import *
from LabelSlider import *


class VeroMixPlasmoid(plasmascript.Applet):
    nowplaying_player_added = pyqtSignal(QString, QObject)
    nowplaying_player_removed = pyqtSignal(QString )
    
    
    volume_high = KIcon("audio-volume-high")
    volume_muted = KIcon("audio-volume-muted")    
    Stopped, Playing, Paused, NA = range(4)  
    
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
        
        self.createDbusServiceDescription()
        
        self.setHasConfigurationInterface(False)
        self.setAspectRatioMode(Plasma.IgnoreAspectRatio)
        self.theme = Plasma.Svg(self)
        
        self.widget = VeroMix(self)            
        self.widget.init()       
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
            self.setPopupIcon(self.volume_high)
            # dont know why but adding it a second time helps (otherwise it 
            # wont popup when you add it directly to the panel)
            self.setGraphicsWidget(self.widget)
            self.connect(self.applet, SIGNAL("appletDestroyed(Plasma::Applet*)"), self.doExit)
            self.setBackgroundHints(Plasma.Applet.NoBackground)    
        except AttributeError:
            self.updateMetadataDesktop()
                                                                                                                                                                              
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


    def createDbusServiceDescription(self):
        print "Outputting dbus-servie file"
        service_dir = os.path.join(BaseDirectory.xdg_data_home,"dbus-1/services/")
        self.createDirectory(service_dir)
        # File to create
        fn = service_dir+"org.veromix.pulseaudio.service"

        exec_dir = unicode(self.package().path()) + "dbus-service/VeromixServiceMain.py"

        # File contents
        c = []
        c.append("[D-BUS Service]\n")
        c.append("Name=org.veromix.pulseaudioservice\n")
        c.append("Exec="+exec_dir+"\n")

        # Write file
        try:
            f = open(fn,"w")
            f.writelines(c)
            f.close()
        except:
            print "Problem writing to file: "+fn
            print "Unexpected error:", sys.exc_info()[0]
        commands.getstatusoutput("chmod u+x "+exec_dir)

    def createDirectory(self, d):
        if not os.path.isdir(d):
            try:
                os.makedirs(d)
            except:
                print "Problem creating directory: "+d
                print "Unexpected error:", sys.exc_info()[0]

    def updateMetadataDesktop(self):
        self.layout = QGraphicsLinearLayout(Qt.Vertical)
        self.setLayout(self.layout)
        icon = Plasma.IconWidget("Please remove and re-add myself")
        icon.setIcon(KIcon("info"))
        self.layout.addItem(icon)
        commands.getstatusoutput("cp " + unicode(self.package().path()) + "metadata.desktop.kde4.4 $(kde4-config  --localprefix )share/apps/plasma/plasmoids/veromix-plasmoid/metadata.desktop" )
        commands.getstatusoutput("cp " + unicode(self.package().path()) + "metadata.desktop.kde4.4 $(kde4-config  --localprefix )share/kde4/services/plasma-applet-veromix-plasmoid.desktop" )
        commands.getstatusoutput("kbuildsycoca4" )
        self.showMessage(KIcon("info"),"<b>Configuration updated</b><br/> \
                Because of a known bug in KDE 4.4 initialization of Veromix failed.<br/><br/>\
                A workaround is now installed.<br/><br/>\
                Please <b>remove</b> this applet and <b>add</b> Veromix again to your desktop/panel (alternatively you can restart plasma-desktop).<br/><br/> \
                Sorry for the inconvenience.", Plasma.ButtonOk) 

    def wheelEvent(self, event):
        self.widget.on_step_volume( (event.delta() > 0) )

    def mousePressEvent(self, event):
        if event.button() == Qt.MidButton:
            self.widget.on_toggle_mute()        

### now playing
             
    def initNowPlaying(self):
        self.player = u''
        self.artist = u''
        self.album = u''
        self.title = u''
        self.volume = 1000
        self.position = 0
        self.length = 0
        self.state = VeroMixPlasmoid.NA
        self.rocking = None
        
        self.now_playing_engine = self.dataEngine('nowplaying')
        self.connect(self.now_playing_engine, SIGNAL('sourceAdded(QString)'), self.playerAdded)
        self.connect(self.now_playing_engine, SIGNAL('sourceRemoved(QString)'), self.playerRemoved)
        self.connectToNowPlayingEngine()
            
    def connectToNowPlayingEngine(self):
        # get sources and connect
        for source in self.now_playing_engine.sources():
            self.playerAdded(U(source))
        
        
    def old(self):    
        self.connected = False
        self.now_playing_engine.disconnectSource(self.player, self)
        print "current player: ", self.player
        
        ## check if already there
        
        ## 
        
        if not self.now_playing_engine.sources().contains(self.player) and self.now_playing_engine.sources().count() > 0:
            self.player = U(self.now_playing_engine.sources().first())

        # not connected ? - connect
        if self.now_playing_engine.sources().contains(self.player):
            self.now_playing_engine.connectSource(self.player, self, 500)
            try:
                # ok add channell
                self.controller = self.now_playing_engine.serviceForSource(self.player)
                print "got a controller " ,  self.controller, " for player:", self.player 
            except:
                self.controller = None
                print "exception:", self.controller
                return
            if self.controller:
                #self.nowplaying = NowPlaying(self.widget, self.controller)
                                
                #self.controller.startOperationCall(self.controller.operationDescription('next'))
                #self.rocking.controller = self.controller
                #name  = U(self.player)            
                #self.rocking.name = name[name.rfind('.') + 1:].title()
                #self.widget.sinks[-1] = self.rocking
                #self.widget.add_sink_to_layout(self.rocking)
                #self.widget.layout.addItem(self.rocking)
                #self.associateWidgets()
                self.connected = True
        else:
            #print ">>>1>>", self.controller
            self.controller = None
            self.dataUpdated('', {})
  
    def playerAdded(self, player):
        print "playerAdded:", player
        # connect to the player
        self.now_playing_engine.disconnectSource(player, self)
        controller = self.now_playing_engine.connectSource(player, self, 1000)        
        self.nowplaying_player_added.emit(player, controller )
        ## signal we got a new player for name
        #if self.now_playing_engine.sources().count() == 1:
            
            #self.connectToNowPlayingEngine()

    def playerRemoved(self, player):
        ## signal  player removed
        print "playerRemoved:", player
        self.now_playing_engine.disconnectSource(player, self)
        self.nowplaying_player_removed.emit(player)
        #if player == self.player:
            #if self.rocking :
                #self.widget.remove_sink_from_layout(self.rocking)
                #del self.widget.sinks[-1]
                #self.rocking.deleteLater()
                #self.rocking = None                
            #self.connectToNowPlayingEngine()
            
    @pyqtSignature('dataUpdated(const QString&, const Plasma::DataEngine::Data&)')
    def dataUpdated(self, sourceName, data):
        #if self.rocking:
            #self.rocking.update_with_info(data)
        #print "data updated"
        pass
    
def U(s):
    # For some reason in Arch Linux & Gentoo data map is QString => QString
    # and in kubuntu (and C++ plasma) QString => QVariant
    if isinstance(s, QVariant):
        return unicode(s.toString())
    elif isinstance(s, QString):
        return unicode(s)
    elif isinstance(s, QFont):
        return unicode(s.toString())
    elif isinstance(s, QColor):
        return unicode(s.name())
    elif isinstance(s, QLineEdit) or isinstance(s, KLineEdit) or \
         isinstance(s, QStandardItem) or isinstance(s, QListWidgetItem) or \
         isinstance(s, KUrlComboRequester):
        return unicode(s.text())
    elif isinstance(s, KColorCombo):
        return unicode(s.color().name())
    elif s == None:
        return u''
    else:
        return unicode(s)    
    
def CreateApplet(parent):    
    # Veromix is dedicated my girlfriend Vero. 
    return VeroMixPlasmoid(parent)
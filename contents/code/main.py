# -*- coding: utf-8 -*-
# copyright 2009-2011  Nik Lutz nik.lutz@gmail.com
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
# Pulseaudio will (one day) provide their own dbus-interface:
# http://pulseaudio.org/wiki/DBusInterface
#
# The python-interface to pulseaudio is a mix of these two projects:
# https://launchpad.net/earcandy
# https://fedorahosted.org/pulsecaster/
# Thank you guys!
###### December 2009 & July 2010


import commands,dbus

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import uic
from PyKDE4 import plasmascript
from PyKDE4.plasma import Plasma
from PyKDE4.kdeui import KIcon
from PyKDE4.kdeui import KActionCollection
from PyKDE4.kdeui import KAction
from PyKDE4.kdeui import KShortcut
from PyKDE4.kdeui import KKeySequenceWidget
from PyKDE4.kdeui import KPageDialog
from PyKDE4.kdeui import KDialog
from PyKDE4.kdecore import *

from VeroMix import VeroMix
from MediaPlayer import NowPlayingController
from Utils import *

COMMENT=i18n("Veromix is a mixer for the Pulseaudio sound server. ")

class VeroMixPlasmoid(plasmascript.Applet):
    VERSION="0.12.0"

    nowplaying_player_added = pyqtSignal(QString, QObject)
    nowplaying_player_removed = pyqtSignal(QString )
    nowplaying_player_dataUpdated = pyqtSignal(QString, dict)

    def __init__(self,parent,args=None):
        self.engine = None
        self.now_playing_engine = None
        self.louder_action_editor = None
        self.lower_action_editor = None
        self.mute_action_editor = None
        self.card_settings = None
        plasmascript.Applet.__init__(self,parent)

    def init(self):
        plasmascript.Applet.init(self)
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

        defaultSize =  QVariant(QSize (0,0))
        size = self.config().readEntry("size", defaultSize ).toSize()
        if (size != defaultSize) :
            self.widget.setPreferredSize(size.width(), size.height())
        else:
            self.widget.setPreferredSize(400 ,145)

        self.connect(self.widget, SIGNAL("resized()"), self.dialogResized)
        #try:
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
        #except AttributeError , e:
            #print e
            #updateMetadataDesktop(self)

        self.initTooltip()
        self.initShortcuts()
        QTimer.singleShot(1000, self.fixPopupIcon)

    def initShortcuts(self):
        self.actionCollection = KActionCollection(self)
        #self.actionCollection.setConfigGlobal(True)
        self.louder_action = self.actionCollection.addAction("VeromixVolumeUp")
        self.louder_action.setText( i18n("Veromix volume up") )
        self.louder_action.setGlobalShortcut(KShortcut())
        self.louder_action.triggered.connect(self.widget.on_step_volume_up)

        self.lower_action = self.actionCollection.addAction("VeromixVolumeDown")
        self.lower_action.setText(i18n("Veromix volume down"))
        self.lower_action.setGlobalShortcut(KShortcut())
        self.lower_action.triggered.connect(self.widget.on_step_volume_down)

        self.mute_action = self.actionCollection.addAction("VeromixVolumeMute")
        self.mute_action.setText(i18n("Veromix toggle  mute"))
        self.mute_action.setGlobalShortcut(KShortcut())
        self.mute_action.triggered.connect(self.widget.on_toggle_mute)

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
        if self.get_show_toolip():
            Plasma.ToolTipManager.self().show(self.applet)

    @pyqtSlot(name="toolTipAboutToShow")
    def toolTipAboutToShow(self):
        pass

    ## FIXME Looks like a bug in plasma: Only when sending a
    # KIcon instance PopUpApplet acts like a Poppupapplet...
    def fixPopupIcon(self):
        #sink = self.widget.getDefaultSink()
        #if sink:
        self.updateIcon()

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
        self.config_ui.showBackground.setCurrentIndex( self.config().readEntry("background","0").toInt() [0])
        self.config_ui.popupMode.setCurrentIndex( self.config().readEntry("popupMode",False).toInt() [0])
        self.config_ui.useTabs.setChecked(self.useTabs())
        self.config_ui.show_tooltip.setChecked(self.get_show_toolip())
        self.config_ui.always_show_sources.setChecked(self.get_always_show_sources())
        self.config_ui.meter_visible.setChecked(self.get_meter_visible())

        self.config_ui.version.setText(VeroMixPlasmoid.VERSION)
        parent.addPage(self.config_widget, i18n("Appearance"), "veromix-plasmoid-128")

        self.mediaplayer_settings_widget = QWidget(parent)
        self.mediaplayer_settings_ui = uic.loadUi(str(self.package().filePath('ui', 'nowplaying.ui')), self.mediaplayer_settings_widget)

        self.mediaplayer_settings_ui.mediaplayerBlacklist.setPlainText(self.get_mediaplayer_blacklist_string())
        self.mediaplayer_settings_ui.runningMediaplayers.setPlainText(self.get_running_mediaplayers())
        self.mediaplayer_settings_ui.runningMediaplayers.setReadOnly(True)

        self.mediaplayer_settings_ui.use_nowplaying.setChecked(self.is_nowplaying_enabled())
        self.mediaplayer_settings_ui.use_nowplaying.stateChanged.connect(self.update_mediaplayer_settings_ui)

        self.mediaplayer_settings_ui.use_mpris2.setChecked(self.is_mpris2_enabled())
        self.mediaplayer_settings_ui.use_mpris2.stateChanged.connect(self.update_mediaplayer_settings_ui)

        parent.addPage(self.mediaplayer_settings_widget, i18n("Media Player Controls"), "veromix-plasmoid-128")

        #self.about_widget = QWidget(parent)
        #self.about_ui = uic.loadUi(str(self.package().filePath('ui', 'about.ui')), self.about_widget)
        #self.about_ui.version.setText(VeroMixPlasmoid.VERSION)
        #parent.addPage(self.about_widget, "About", "help-about" )
        self.add_audio_settings(parent)
        self.add_global_shortcut_page(parent)

        # FIXME KDE 4.6 workaround
        self.connect(parent, SIGNAL("okClicked()"), self.configChanged)
        self.connect(parent, SIGNAL("cancelClicked()"), self.configDenied)
        return self.config_widget

    def add_audio_settings(self, dialog):
        self.audio_settings_page = QWidget()
        layout = QGridLayout()
        self.audio_settings_page.setLayout(layout)

        self.max_volume_spinbox = QSpinBox()
        self.max_volume_spinbox.setRange(1,255)
        self.max_volume_spinbox.setSingleStep(1)
        self.max_volume_spinbox.setValue(self.get_max_volume_value())
        layout.addWidget(QLabel(i18n("Max volume value")), 0,0)
        layout.addWidget(self.max_volume_spinbox, 0,1)

        self.automute_checkbox = QCheckBox()
        self.automute_checkbox.setChecked(self.get_auto_mute())
        layout.addWidget(QLabel(i18n("Mute if volume reaches zero")), 1,0)
        layout.addWidget(self.automute_checkbox, 1,1)

        layout.addItem(QSpacerItem(0,20, QSizePolicy.Minimum,QSizePolicy.Fixed ), 2,0)
        layout.addWidget(QLabel("<b>"+i18n("Sound Card Profiles")+"</b>"), 3,0)
        index=4
        self.card_settings = {}
        for card in self.widget.card_infos.values():
            combo = QComboBox()
            #self.automute_checkbox.setChecked(self.get_auto_mute())
            #print card.properties
            layout.addWidget(QLabel(card.properties[dbus.String("device.description")]), index,0)
            layout.addWidget(combo, index,1)
            index = index + 1

            self.card_settings[combo] = card
            profiles = card.get_profiles()
            active = card.get_active_profile_name()
            active_index = 0
            for profile in profiles:
                combo.addItem(profile.description)
                if active == profile.name:
                    active_index = profiles.index(profile)
            combo.setCurrentIndex(active_index)

        layout.addItem(QSpacerItem(0,0, QSizePolicy.Minimum,QSizePolicy.Expanding ), index,0)
        dialog.addPage(self.audio_settings_page, i18n("Pulseaudio"), "preferences-desktop-sound")

    # anybody knows how to remove/extend the default shortcuts page?
    def add_global_shortcut_page(self,dialog):
        self.kb_settings_page = QWidget()

        layout = QGridLayout()
        self.kb_settings_page.setLayout(layout)

        self.louder_action_editor = KKeySequenceWidget()
        self.louder_action_editor.setKeySequence( self.louder_action.globalShortcut().primary())
        layout.addWidget(QLabel(i18n("Veromix volume up")), 0,0)
        layout.addWidget(self.louder_action_editor, 0,1)

        self.lower_action_editor = KKeySequenceWidget()
        self.lower_action_editor.setKeySequence( self.lower_action.globalShortcut().primary())
        layout.addWidget(QLabel(i18n("Veromix volume down")), 1, 0)
        layout.addWidget(self.lower_action_editor, 1, 1)

        self.mute_action_editor = KKeySequenceWidget()
        self.mute_action_editor.setKeySequence( self.mute_action.globalShortcut().primary())
        layout.addWidget(QLabel(i18n("Veromix toggle  mute")), 2, 0)
        layout.addWidget(self.mute_action_editor, 2, 1)

        layout.addItem(QSpacerItem(0,0, QSizePolicy.Minimum,QSizePolicy.Expanding ), 3,0)
        dialog.addPage(self.kb_settings_page, i18n("Keyboard Shortcuts"), "preferences-desktop-keyboard")

    def configDenied(self):
        self.apply_nowplaying(self.is_nowplaying_enabled())
        self.apply_mpris2(self.is_mpris2_enabled())

    def configChanged(self):
        self.config().writeEntry("background",str(self.config_ui.showBackground.currentIndex()))
        self.config().writeEntry("popupMode", str(self.config_ui.popupMode.currentIndex()))
        tabs = self.useTabs()
        self.config().writeEntry("useTabs", bool(self.config_ui.useTabs.isChecked()))
        self.config().writeEntry("show_tooltip", bool(self.config_ui.show_tooltip.isChecked()))
        self.config().writeEntry("always_show_sources", bool(self.config_ui.always_show_sources.isChecked()))

        meter_visible = self.get_meter_visible()
        self.config().writeEntry("meter_visible", bool(self.config_ui.meter_visible.isChecked()))

        self.config().writeEntry("use_nowplaying", str(self.mediaplayer_settings_ui.use_nowplaying.isChecked()))
        self.config().writeEntry("use_mpris2", str(self.mediaplayer_settings_ui.use_mpris2.isChecked()))

        #self.config().writeEntry("mpris2List",str(self.mediaplayer_settings_ui.mpris2List.toPlainText()).strip())
        self.config().writeEntry("nowplayingBlacklist",str(self.mediaplayer_settings_ui.mediaplayerBlacklist.toPlainText()).strip())

        self.config().writeEntry("max_volume", str(self.max_volume_spinbox.value()))
        self.config().writeEntry("auto_mute", str(self.automute_checkbox.isChecked()))

        self.applyConfig()

        if tabs != self.useTabs():
            self.widget.switchView()
        self.widget.on_update_configuration()

    def update_mediaplayer_settings_ui(self):
        enable = ( self.mediaplayer_settings_ui.use_nowplaying.isChecked() or self.mediaplayer_settings_ui.use_mpris2.isChecked())
        self.mediaplayer_settings_ui.mediaplayerBlacklist.setEnabled(enable)
        self.mediaplayer_settings_ui.mediaplayerBlacklistLabel.setEnabled(enable)
        self.mediaplayer_settings_ui.runningMediaplayers.setEnabled(enable)
        self.mediaplayer_settings_ui.runningMediaplayersLabel.setEnabled(enable)
        self.mediaplayer_settings_ui.runningMediaplayers.setPlainText(self.get_running_mediaplayers())

    def apply_nowplaying(self, enabled):
        self.disable_nowplaying()
        if enabled:
            self.init_nowplaying()

    def apply_mpris2(self, enabled):
        self.widget.pa.disable_mpris2()
        self.remove_mpris2_widgets()
        if enabled:
            self.widget.pa.enable_mpris2()
            self.init_running_mpris2()

    def applyConfig(self):
        self.apply_nowplaying(self.is_nowplaying_enabled() )
        self.apply_mpris2(self.is_mpris2_enabled() )

        bg = self.config().readEntry("background","0").toInt()[0]
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

        if self.louder_action_editor:
            sequence = self.louder_action_editor.keySequence()
            if sequence != self.louder_action.globalShortcut().primary():
                self.louder_action.setGlobalShortcut(KShortcut(sequence), KAction.ActiveShortcut, KAction.NoAutoloading )
        if self.lower_action_editor:
            sequence = self.lower_action_editor.keySequence()
            if sequence != self.lower_action.globalShortcut().primary():
                self.lower_action.setGlobalShortcut(KShortcut(sequence), KAction.ActiveShortcut, KAction.NoAutoloading )
        if self.mute_action_editor:
            sequence = self.mute_action_editor.keySequence()
            if sequence != self.mute_action.globalShortcut().primary():
                self.mute_action.setGlobalShortcut(KShortcut(sequence), KAction.ActiveShortcut, KAction.NoAutoloading )

        if self.card_settings:
            for combo in self.card_settings.keys():
                card = self.card_settings[combo]
                for profile in card.profiles:
                    if combo.currentText() == profile.description:
                        self.widget.pa.set_card_profile(card.index, profile.name)
        self.update()

    def configWidgetDestroyed(self):
        self.config_widget = None
        self.config_ui = None

    def useTabs(self):
        return self.config().readEntry("useTabs",False ).toBool()

    def get_meter_visible(self):
        return self.config().readEntry("meter_visible",True ).toBool()

    def get_auto_mute(self):
        return self.config().readEntry("auto_mute",False ).toBool()

    def get_show_toolip(self):
        return self.config().readEntry("show_tooltip",True ).toBool()

    def get_always_show_sources(self):
        return self.config().readEntry("always_show_sources",False ).toBool()

    def get_max_volume_value(self):
        default = 100
        return self.config().readEntry("max_volume",default ).toInt()[0]

### now playing

    def is_nowplaying_enabled(self):
        return self.config().readEntry("use_nowplaying",False).toBool()

    def is_mpris2_enabled(self):
        return self.config().readEntry("use_mpris2",True).toBool()

    def disable_nowplaying(self):
        for player in self.widget.get_mediaplayer_widgets():
            if player.is_nowplaying_player():
                self.on_nowplaying_player_removed(player.controller_name())
        self.now_playing_engine = None

    def remove_mpris2_widgets(self):
        for player in self.widget.get_mediaplayer_widgets():
            if player.is_mpris2_player():
                self.on_mpris2_removed(player.controller_name())

    def init_nowplaying(self):
        self.now_playing_engine = self.dataEngine('nowplaying')
        self.connect(self.now_playing_engine, SIGNAL('sourceAdded(QString)'), self.on_nowplaying_player_added)
        self.connect(self.now_playing_engine, SIGNAL('sourceRemoved(QString)'), self.on_nowplaying_player_removed)
        self.connect_to_nowplaying_engine()

    def init_running_mpris2(self):
        for controller in self.widget.pa.get_mpris2_players():
            v= controller.name()
            if self.in_mediaplayer_blacklist(v):
                return
            self.nowplaying_player_added.emit(controller.name(), controller )

    def connect_to_nowplaying_engine(self):
        # get sources and connect
        for source in self.now_playing_engine.sources():
            self.on_nowplaying_player_added(source)

    def on_nowplaying_player_added(self, player):
        if player == "players":
            # FIXME 4.6 workaround
            return
        if self.in_mediaplayer_blacklist(player):
            return
        self.now_playing_engine.disconnectSource(player, self)
        self.now_playing_engine.connectSource(player, self, 2000)
        controller = self.now_playing_engine.serviceForSource(player)
        self.nowplaying_player_added.emit(player, NowPlayingController(self.widget,controller) )

    def in_mediaplayer_blacklist(self,player):
        for entry in self.get_mediaplayer_blacklist():
            if str(player).find(entry) == 0:
                return True
        return False

    def on_nowplaying_player_removed(self, player):
        if self.now_playing_engine:
            self.now_playing_engine.disconnectSource(player, self)
            self.nowplaying_player_removed.emit(player)

    def on_mpris2_removed(self, player):
        self.nowplaying_player_removed.emit(player)

    def get_running_mediaplayers(self):
        val = "nowplaying:\n"
        engine =  self.now_playing_engine
        if engine == None:
            engine = self.dataEngine('nowplaying')
        for source in engine.sources():
            val += source + "\n"
        val += "\nmpris2:\n"
        for controller in self.widget.pa.get_mpris2_players():
            val += controller.name() + "\n"
        return val

    def get_mediaplayer_blacklist(self):
        return self.get_mediaplayer_blacklist_string().split("\n")

    def get_mediaplayer_blacklist_string(self):
        default =  "org.mpris.bangarang"
        return self.config().readEntry("nowplayingBlacklist",default ).toString()

    @pyqtSignature('dataUpdated(const QString&, const Plasma::DataEngine::Data&)')
    def dataUpdated(self, sourceName, data):
        self.nowplaying_player_dataUpdated.emit(sourceName, data)


def CreateApplet(parent):
    # Veromix is dedicated to my girlfriend Vero.
    return VeroMixPlasmoid(parent)

# -*- coding: utf-8 -*-
# copyright 2009  Nik Lutz
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

import dbus,  os, datetime

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyKDE4.kdeui import *
from PyKDE4.plasma import Plasma

from LabelSlider import LabelSlider
from LabelSlider import Label
from Channel import Channel
from PulseAudioProxy import Mpris2DummyController
from MuteButton  import *

#class ExtensionWidgetQGraphicsWidget):

    #def __init__(controller):
        #self.controller = controller
        #self.init()
        #self.compose_arrangement()

    #def init(self):
        #self.init_arrangement()

    #def init_arrangement(self):
        #self.layout = QGraphicsLinearLayout(Qt.Horizontal)
        #self.layout.setContentsMargins(0,0,0,0)
        #self.setLayout(self.layout)
        
    #def compose_arrangement(self):
        #pass

    #def update_with_info(self, info):
        #pass


#class NowPlayingExtended(ExtensionWidgetQGraphicsWidget):
    #pass

   
class MediaPlayerUI( Channel ):
    Stopped, Playing, Paused, NA = range(4)

    def __init__(self,name, veromix, controller):
        self.controller = controller
        Channel.__init__(self, veromix)
        self.index = -1

        self.state = MediaPlayerUI.NA
        self.position = 0
        self.length = 0
        self.artwork = ""
        self.cover_string = ""
        self.last_playing_icon = KIcon(self.get_pauseIcon())
        self.layout.setContentsMargins(6,0,6,2)
        self.name = name
        self.connect_mpris2()
        self.connect_nowplaying()
        
    def initArrangement(self):
        self.svg_path = self.veromix.applet.package().filePath('images', 'buttons.svgz')
        self.createMiddle()
        self.createSlider()
        self.create_prev_panel()
        self.create_frame()
        self.create_panel()
        self.create_prev_button()
        self.create_play_pause_button()
        self.create_next_button()
        self.create_next_panel()
        self.createPositionLabel()
        self.createLengthLabel()
        self.create_expander()

    def composeArrangement(self):
        self.layout.addItem(self.frame)
        self.frame_layout.addItem(self.panel)
        self.prev_panel_layout.addStretch()
        self.prev_panel_layout.addItem(self.prev)
        self.next_panel_layout.addStretch()
        self.next_panel_layout.addItem(self.next)
        self.prev_panel.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        self.next_panel.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))        
        self.play.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.middle_layout.addStretch()
        self.middle_layout.addItem(self.play)
        self.panel.setContentsMargins(0,0,0,0)
        self.panel_layout.setContentsMargins(6,0,10,6)
        self.panel_layout.addStretch()
        self.panel_layout.addItem(self.prev_panel)
        self.panel_layout.addItem(self.middle)
        self.panel_layout.addItem(self.next_panel)
        self.panel_layout.addStretch()

    def on_expander_clicked(self):
        self.middle_layout.removeItem(self.slider)
        if (self.extended_panel_shown):
            self.extended_panel_shown = False
            self.frame_layout.removeItem(self.extended_panel)
            self.extended_panel = None
            self.slider= None
        else:
            self.extended_panel_shown = True
            self.create_settings_widget()
            self.get_dbus_info()
            self.frame_layout.addItem(self.extended_panel)

    def create_settings_widget(self):
        self.createLengthLabel()
        self.createPositionLabel()
        self.createSlider()
        self.extended_panel = QGraphicsWidget()
        self.extended_panel_layout = QGraphicsLinearLayout(Qt.Horizontal)
        self.extended_panel_layout.setContentsMargins(0,0,0,0)
        self.extended_panel.setLayout(self.extended_panel_layout)

        self.extended_panel_layout.addStretch()
        self.extended_panel_layout.addItem(self.position_label)
        self.extended_panel_layout.addItem(self.slider)
        self.extended_panel_layout.addItem(self.length_label)
        self.extended_panel_layout.addStretch()
## data input

    def update_with_info(self, data):
        self.update_state(data)
        self.update_cover(data)
        self.updateSortOrderIndex()
        if self.extended_panel_shown:
            self.update_position(data)
            self.update_slider()

    def on_update_configuration(self):
        pass

## update ui

    def update_state(self,data):
        state = self.state
        if QString('State') in data:
            if data[QString('State')] == u'playing':
                state = MediaPlayerUI.Playing
            else:
                state = MediaPlayerUI.Paused
        if self.state != state:
            self.state = state
            if self.state == MediaPlayerUI.Playing:
                #self.play.setSvg(self.svg_path, "pause-normal")
                self.play.setIcon(KIcon("media-playback-pause"))
                self.middle.setIcon(self.last_playing_icon)
            else:
                #self.play.setSvg(self.svg_path, "play-normal")
                self.play.setIcon(KIcon("media-playback-start"))
                self.middle.setIcon(KIcon(self.get_pauseIcon()))

    def update_cover(self,data):
        if QString('Artwork') in data:
            val = data[QString('Artwork')]
            if self.artwork !=  val:
                self.artwork = val
                if val == None:
                    self.last_playing_icon = KIcon(self.get_pauseIcon())
                else:
                    self.last_playing_icon = QIcon(QPixmap(self.artwork))
                self.middle.setIcon(self.last_playing_icon)

    def update_position(self, data):
        if QString('Position') in data:
            v = data[QString('Position')]
            if v != self.position:
                self.position = v
                pos_str = ( '%d:%02d' % (v / 60, v % 60))
                self.position_label.setText(pos_str)
        if QString('Length') in data:
            v = data[QString('Length')]
            if v != self.length:
                self.length = v
                pos_str = ( '%d:%02d' % (v / 60, v % 60))
                self.length_label.setText(pos_str)

    def update_slider(self):
        if self.slider and self.extended_panel_shown:
            if self.state == MediaPlayerUI.Stopped:
                self.slider.setValue(0)
            else:
                self.slider.setMaximum(self.length)
                self.slider.setValue(self.position)
        
## initialize ui

    def create_next_panel(self):
        self.next_panel = QGraphicsWidget()
        self.next_panel_layout = QGraphicsLinearLayout(Qt.Vertical)
        self.next_panel_layout.setContentsMargins(0,0,0,0)
        self.next_panel.setLayout(self.next_panel_layout)

    def createPositionLabel(self):
        self.position_label = Label()
        self.position_label.setContentsMargins(0,0,0,0)
        self.position_label.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding, True))
        self.position_label.setAlignment(Qt.AlignRight)

    def createLengthLabel(self):
        self.length_label = Label()
        self.length_label.setContentsMargins(0,0,0,0)
        self.length_label.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding, True))
        self.length_label.setAlignment(Qt.AlignLeft)

    def create_prev_panel(self):
        self.prev_panel = Plasma.IconWidget()
        self.prev_panel_layout = QGraphicsLinearLayout(Qt.Vertical)
        self.prev_panel_layout.setContentsMargins(0,0,0,0)
        self.prev_panel.setLayout(self.prev_panel_layout)
        self.prev_panel.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum))

    def createMiddle(self):
        self.middle = Plasma.IconWidget()
        self.middle_layout = QGraphicsLinearLayout(Qt.Vertical)
        self.middle_layout.setContentsMargins(0,0,0,0)
        self.middle.setLayout(self.middle_layout)
        self.CONTROLSBAR_SIZE = 80
        self.setMinimumHeight(self.CONTROLSBAR_SIZE)
        self.setPreferredHeight(self.CONTROLSBAR_SIZE)
        self.setMaximumHeight(self.CONTROLSBAR_SIZE)        
        self.middle.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        self.middle.setIcon(KIcon(self.get_pauseIcon()))
        self.middle.clicked.connect(self.on_play_cb)

    def create_next_button(self):
        self.next = MuteButton(self)
        self.next.setAbsSize(20)
        #self.next.setSvg(self.svg_path , "next-normal")
        self.next.setIcon(KIcon("media-skip-forward"))
        self.connect(self.next, SIGNAL("clicked()"), self.on_next_cb  )

    def create_prev_button(self):
        self.prev = MuteButton(self)
        self.prev.setAbsSize(20)
        #self.prev.setSvg(self.svg_path, "prev-normal")
        self.prev.setIcon(KIcon("media-skip-backward"))
        self.connect(self.prev, SIGNAL("clicked()"), self.on_prev_cb  )

    def create_play_pause_button(self):
        self.play = MuteButton(self)
        self.play.setAbsSize(-1)
        #self.play.setSvg(self.svg_path, "stop-normal")
        self.play.setIcon(KIcon("media-playback-stop"))
        self.connect(self.play, SIGNAL("clicked()"), self.on_play_cb  )

    def createMute(self):
        pass

    def createMeter(self):
        pass

# callbacks

    def on_mute_cb(self):
        pass

    def on_next_cb(self):
        self.controller.startOperationCall(self.controller.operationDescription('next'))

    def on_prev_cb(self):
        self.controller.startOperationCall(self.controller.operationDescription('previous'))

    def on_play_cb(self):
        if not self.veromix.pa:
            return
        if self.state == MediaPlayerUI.Playing:
            self.controller.startOperationCall(self.controller.operationDescription('pause'))
        else:
            self.controller.startOperationCall(self.controller.operationDescription('play'))

    def on_slider_cb(self, value):
        pass

# nowplaying

    def connect_nowplaying(self):
        if self.is_nowplaying_player() :
            self.veromix.applet.nowplaying_player_dataUpdated.connect(self.on_nowplaying_data_updated)
        
    def on_nowplaying_data_updated(self, name, values):
        if name == self.controller.destination():
            self.update_with_info(values)
            
# dbus

    def connect_mpris2(self):
        if self.is_mpris2_player() :
            if self.veromix.pa:
                self.veromix.pa.connect_mpris2_player(self.on_mpris2_properties_changed, str(self.controller.destination()) )
                self.get_dbus_info()
                
    def on_mpris2_properties_changed(self, interface, properties, signature):
        data = {}
        if dbus.String("PlaybackStatus") in properties.keys():
            status = properties[dbus.String("PlaybackStatus")]
            data[QString('State')] =  u'paused'
            if status == 'Playing':
                data[QString('State')] =  u'playing'
        
        if dbus.String("Metadata") in properties.keys():
            metadata = properties[dbus.String("Metadata")]
            if dbus.String("mpris:artUrl") in metadata.keys():
                val = QUrl(str(metadata[dbus.String("mpris:artUrl")])).path()
                if val != self.cover_string:
                    if (os.path.isfile(val)):
                        data[QString('Artwork')] =  QPixmap(val)
                    else:
                        data[QString('Artwork')] = None
                    self.cover_string = val
            if dbus.String("mpris:length") in metadata.keys():
                data[QString('Length')] = metadata[dbus.String("mpris:length")] / 1000000
                 
        if QString('Position') in properties.keys():
            data[QString('Position')] = properties[QString('Position')] / 1000000
        self.update_with_info(data)

    def get_dbus_info(self):
        ## FIXME fetch info can call on_mpris2_properties_changed
        data = {}
        if self.is_nowplaying_player():
            return
        if not self.veromix.pa:
            return
        properties = {}
        properties[dbus.String("PlaybackStatus")] =self.veromix.pa.mpris2_get_playback_status(self.controller.destination())
        properties[dbus.String("Metadata")] = self.veromix.pa.mpris2_get_metadata(self.controller.destination())
        #print properties[dbus.String("Metadata")]
        self.length = -1
        self.position = -1 
        self.fetch_position()
        self.on_mpris2_properties_changed(None, properties, None)


    def fetch_position(self):
        if self.extended_panel_shown:
            properties = {}
            properties[QString('Position')] = self.veromix.pa.mpris2_get_position(self.controller.destination())
            self.on_mpris2_properties_changed(None, properties, None)
            QTimer.singleShot(1000, self.fetch_position)

# helpers

    def get_pauseIcon(self):
        name = self.get_application_name()
        app = self.veromix.query_application(str(name))
        if app == None:
            return name
        return app
        
    def get_application_name(self):
        name = self.controller.destination()
        if name.indexOf("org.mpris.MediaPlayer2.")  == 0:
            return name[23:]
        if name.indexOf("org.mpris.")  == 0:
            return name[10:]
        return name

    def matches(self, sink):
        sink = self.get_assotiated_sink()
        if sink == None:
            return False
        return True

    def get_assotiated_sink(self):
        name = str(self.get_application_name()).lower()
        for sink in self.veromix.get_sinkinput_widgets():
            if str(sink.text).lower() == name:
                return sink
        for sink in self.veromix.get_sinkinput_widgets():
            if str(sink.text).lower().find(name) >= 0 :
                return sink
        return None

## overrides

    def isNowplaying(self):
        return True

    def isSinkOutput(self):
        return False

    def isSinkInput(self):
        return False

    def updateSortOrderIndex(self):
        sink = self.get_assotiated_sink()
        if sink != None:
            new =  sink.sortOrderIndex - 1
            if self.sortOrderIndex != new:
                self.sortOrderIndex = new

## testing

    def is_nowplaying_player(self):
        return not self.is_mpris2_player()

    def is_mpris2_player(self):
        # FIXME
        return isinstance(self.controller, Mpris2DummyController)
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
from MuteButton  import *

class NowPlaying( Channel ):
    Stopped, Playing, Paused, NA = range(4)

    def __init__(self,veromix, controller):
        self.controller = controller
        Channel.__init__(self, veromix)
        self.index = -1
        self.state = NowPlaying.NA
        self.position = 0
        self.length = 0
        self.artwork = ""
        self.cover_string = ""
        self.last_playing_icon = KIcon(self.getPauseIcon())
        self.layout.setContentsMargins(6,0,6,2)
        self.name = "nowplaying"
        self.connect_mpris2()
        
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
        self.panel_layout.addStretch()
        self.panel_layout.addItem(self.prev_panel)
        self.panel_layout.addItem(self.middle)
        self.panel_layout.addItem(self.next_panel)
        self.panel_layout.addStretch()

    def connect_mpris2(self):
        if self.use_dbus_workaround:
            if self.veromix.pa:
                self.veromix.pa.connect_mpris2_player(self.on_mpris2_properties_changed, str(self.controller.destination()) )
        self.get_dbus_info()

    def update_with_info(self, data):
        self.update_state(data)
        self.update_cover(data)
        self.updateSortOrderIndex()

    def update_state(self,data):
        state = self.state
        if QString('State') in data:
            if data[QString('State')] == u'playing':
                state = NowPlaying.Playing
            else:
                state = NowPlaying.Paused
        if self.state != state:
            self.state = state
            if self.state == NowPlaying.Playing:
                #self.play.setSvg(self.svg_path, "pause-normal")
                self.play.setIcon(KIcon("media-playback-pause"))
                self.middle.setIcon(self.last_playing_icon)
            else:
                #self.play.setSvg(self.svg_path, "play-normal")
                self.play.setIcon(KIcon("media-playback-start"))

    def getPauseIcon(self):
        name = self.get_application_name()
        app = self.veromix.query_application(str(name))
        if app == None:
            return name
        return app

    def update_cover(self,data):
        ## FIXME
        #if self.state == NowPlaying.Paused  :
            #if self.artwork != None:
                #self.artwork = None
                #self.middle.setIcon(KIcon(self.getPauseIcon()))
            #print "paused no cover"
            #return
        if QString('Artwork') in data:
            val = data[QString('Artwork')]
            if self.artwork !=  val:
                self.artwork = val
                if val == None:
                    self.last_playing_icon = KIcon(self.getPauseIcon())
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
                self.positionLabel.setText(pos_str)

    def createMeter(self):
        pass

    def create_next_panel(self):
        self.next_panel = QGraphicsWidget()
        self.next_panel_layout = QGraphicsLinearLayout(Qt.Vertical)
        self.next_panel_layout.setContentsMargins(0,0,0,0)
        self.next_panel.setLayout(self.next_panel_layout)

    def createPositionLabel(self):
        self.positionLabel = Label()
        self.positionLabel.setContentsMargins(0,0,0,0)
        self.positionLabel.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding, True))
        self.positionLabel.setAlignment(Qt.AlignRight)

    def createLengthLabel(self):
        self.position_label = Label()
        self.position_label.setContentsMargins(0,0,0,0)
        self.position_label.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding, True))
        self.position_label.setAlignment(Qt.AlignLeft)

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
        self.CONTROLSBAR_SIZE = 112
        self.setMinimumHeight(self.CONTROLSBAR_SIZE)
        self.setPreferredHeight(self.CONTROLSBAR_SIZE)
        self.setMaximumHeight(self.CONTROLSBAR_SIZE)        
        self.middle.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        self.middle.setIcon(KIcon(self.getPauseIcon()))
        self.middle.clicked.connect(self.on_play_cb)

    def createMute(self):
        pass

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

    def on_mute_cb(self):
        pass

    def on_next_cb(self):
        if not self.veromix.pa:
            return
        if self.use_dbus_workaround():
            self.veromix.pa.nowplaying_next(self.controller.destination())
        else:
            self.controller.startOperationCall(self.controller.operationDescription('next'))

    def on_prev_cb(self):
        if not self.veromix.pa:
            return
        if self.use_dbus_workaround():
            self.veromix.pa.nowplaying_prev(self.controller.destination())
        else:
            self.controller.startOperationCall(self.controller.operationDescription('previous'))

    def on_play_cb(self):
        if not self.veromix.pa:
            return
        if self.state == NowPlaying.Playing:
            if self.use_dbus_workaround():
                self.veromix.pa.nowplaying_pause(self.controller.destination())
            else:
                self.controller.startOperationCall(self.controller.operationDescription('pause'))
        else:
            if self.use_dbus_workaround():
                self.veromix.pa.nowplaying_play(self.controller.destination())
            else:
                self.controller.startOperationCall(self.controller.operationDescription('play'))

    def on_slider_cb(self, value):
        pass

    def use_dbus_workaround(self):
        for name in self.get_mpris2_clients():
            if str(self.controller.destination()) .find(name) == 0:
                return True
        False

    def get_mpris2_clients(self):
        return self.veromix.applet.getMpris2Clients()

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
        self.update_with_info(data)

    def get_dbus_info(self):
        ## FIXME fetch info can call on_mpris2_properties_changed
        data = {}
        if not self.veromix.pa:
            return 
        status = self.veromix.pa.nowplaying_getPlaybackStatus(self.controller.destination())
        data[QString('State')] =  u'paused'
        if status == 'Playing':
            data[QString('State')] =  u'playing'
        metadata = self.veromix.pa.nowplaying_getMetadata(self.controller.destination())
        if dbus.String("mpris:artUrl") in metadata.keys():
            val = QUrl(str(metadata[dbus.String("mpris:artUrl")])).path()
            if val != self.cover_string:
                if (os.path.isfile(val)):
                    data[QString('Artwork')] =  QPixmap(val)
                else:
                    data[QString('Artwork')] = None
                self.cover_string = val
        #if dbus.String("mpris:length") in metadata.keys():
            #v =  int(metadata[str(dbus.String("mpris:length"))])  / 1000000
            #data[QString('Length')] = v
        #data[QString('Position')] = int(self.veromix.pa.nowplaying_getPosition(self.controller.destination()))  / 1000000
        self.update_with_info(data)

    def get_application_name(self):
        name = self.controller.destination()
        if name.indexOf("org.mpris.MediaPlayer2.")  == 0:
            return name[23:]
        if name.indexOf("org.mpris.")  == 0:
            return name[10:]
        return name

    def updateSortOrderIndex(self):
        sink = self.get_assotiated_sink()
        if sink != None:
            new =  sink.sortOrderIndex - 1
            if self.sortOrderIndex != new:
                self.sortOrderIndex = new

    def matches(self, sink):
        sink = self.get_assotiated_sink()
        if sink == None:
            return False
        return True

    def get_assotiated_sink(self):
        name = str(self.get_application_name()).lower()
        for sink in self.veromix.getSinkInputs():
            if str(sink.text).lower() == name:
                return sink
        for sink in self.veromix.getSinkInputs():
            if str(sink.text).lower().find(name) >= 0 :
                return sink
        return None

    def isNowplaying(self):
        return True
# -*- coding: utf-8 -*-
# copyright 20011  Nik Lutz
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
from MediaPlayer import *


class MediaPlayerUI( Channel ):

    def __init__(self,name, veromix, controller):
        self.controller = controller
        Channel.__init__(self, veromix)
        self.controller.data_updated.connect(self.controller_data_updated)
        self.index = -1

        self._state= None
        self._position = 0
        self._length = 0
        self._artwork = ""

        self.last_playing_icon = KIcon(self.get_pauseIcon())
        self.layout.setContentsMargins(6,0,6,2)

        self.controller.init_connection()

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
            self.frame_layout.addItem(self.extended_panel)
        self.controller.set_fetch_extended_info(self.extended_panel_shown)

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

    def controller_data_updated(self):
        self.update_state()
        self.update_cover()
        self.updateSortOrderIndex()
        if self.extended_panel_shown:
            self.update_position()
            self.update_slider()

    def on_update_configuration(self):
        pass

## update ui

    def update_state(self):
        state = self.controller.state()
        if self._state != state:
            self._state = state
            if state == MediaPlayer.Playing:
                #self.play.setSvg(self.svg_path, "pause-normal")
                self.play.setIcon(KIcon("media-playback-pause"))
                self.middle.setIcon(self.last_playing_icon)
            else:
                #self.play.setSvg(self.svg_path, "play-normal")
                self.play.setIcon(KIcon("media-playback-start"))
                self.middle.setIcon(KIcon(self.get_pauseIcon()))

    def update_cover(self):
        # FIXME
        val = self.controller._cover_string
        if self._artwork !=  val:
            self._artwork = val
            if val == None:
                self.last_playing_icon = KIcon(self.get_pauseIcon())
            else:
                self.last_playing_icon = QIcon(QPixmap(self.controller.artwork()))
            self.middle.setIcon(self.last_playing_icon)

    def update_position(self):
        v = self.controller.position()
        if v != self._position:
            self._position = v
            pos_str = ( '%d:%02d' % (v / 60, v % 60))
            self.position_label.setBoldText(pos_str)
        v = self.controller.length()
        if v != self._length:
            self._length = v
            pos_str = ( '%d:%02d' % (v / 60, v % 60))
            self.length_label.setBoldText(pos_str)

    def update_slider(self):
        if self.slider and self.extended_panel_shown:
            if self.controller.state() == MediaPlayer.Stopped:
                self.slider.setValueFromPulse(0)
            else:
                if self.controller.length() > -1 :
                    v = self.controller.position() * 100 / self.controller.length()
                    if self.slider.check_pulse_timestamp():
                        self.slider.setValue(v)

    def on_slider_action_triggered(self, action):
        value = self.slider.nativeWidget().sliderPosition()
        if value > -1 and action == 7:
            self.controller.seek(value)

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
        self.controller.next_track()

    def on_prev_cb(self):
        self.controller.prev_track()

    def on_play_cb(self):
        if self.controller.state() == MediaPlayer.Playing:
            self.controller.pause()
        else:
            self.controller.play()

# helpers

    def controller_name(self):
        return self.controller.name()

    def get_pauseIcon(self):
        name = self.get_application_name()
        app = self.veromix.query_application(str(name))
        if app == None:
            return name
        return app

    def get_application_name(self):
        return self.controller.get_application_name()

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

    def createSlider(self):
        Channel.createSlider(self)
        self.slider.setMaximum(100)
        self.slider.volumeChanged.disconnect(self.on_slider_cb)
        self.slider.nativeWidget ().actionTriggered.connect(self.on_slider_action_triggered)

## testing

    def is_nowplaying_player(self):
        return self.controller.is_mpris2_player()

    def is_mpris2_player(self):
        return self.controller.is_mpris2_player()
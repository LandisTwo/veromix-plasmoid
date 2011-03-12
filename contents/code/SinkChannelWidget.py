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

from PyKDE4.plasma import Plasma
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyKDE4.kdeui import *

from LabelSlider import LabelSlider

class SinkChannelWidget(QGraphicsWidget):

    def __init__(self, veromix, sink):
        QGraphicsWidget.__init__(self)
        self.veromix = veromix
        self.sink = sink
        self.sliders = []
        self.text = ""
        self.bold_text = ""
        self.init()

    def init(self):
        self.init_arrangement()
        self.create_channel_sliders()
        self.create_settings_widget()
        self.compose_arrangement()

    def compose_arrangement(self):
        self.setContentsMargins(0,0,0,0)
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.addItem(self.label)
        self.layout.addItem(self.slider_widget)
        self.adjustSize()

    def init_arrangement(self):
        self.layout = QGraphicsLinearLayout(Qt.Vertical)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed, True))
        self.layout.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed, True))
        self.setLayout(self.layout)

        self.label = Plasma.Label()
        self.label.setAlignment(Qt.AlignTop)
        self.label.setPreferredHeight(12)
        self.label.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed, True))
        self.label.setContentsMargins(0,0,0,0)

    def create_channel_sliders(self):
        self.slider_layout = QGraphicsLinearLayout(Qt.Vertical)
        self.slider_layout.setContentsMargins(0,2,0,0)

        self.slider_widget = QGraphicsWidget()
        self.slider_widget.setLayout(self.slider_layout)
        self.slider_widget.setContentsMargins(0,0,0,0)
        for channel in self.sink.pa_sink.getChannels():
            slider = LabelSlider()
            slider.setOrientation(Qt.Horizontal)
            slider.setText(channel.getName())
            slider.setMaximum(self.veromix.get_max_volume_value())
            slider.setValue(channel.getVolume())
            slider.volumeChanged.connect(self.on_slider_cb)
            self.sliders.append(slider)
            self.slider_layout.addItem(slider)

    def create_settings_widget(self):
        pass

## FIXME
    def setText(self, text):
        if text:
            self.text = text
        self.label.setText( "<b>"+self.bold_text + "</b> " + self.text)

    def setBoldText(self,text):
        if text:
            self.bold_text = text
        self.setText(self.text)

    def update_with_info(self, info):
        self.set_slider_values()

    def set_slider_values(self):
        channels = self.sink.pa_sink.getChannels()
        for i in range(0,len(channels)):
            name = channels[i].getName()
            if name != "None":
                self.sliders[i].setBoldText("")
                self.sliders[i].setText(name)
            self.sliders[i].setValueFromPulse(channels[i].getVolume())

    def on_slider_cb(self, value):
        vol = []
        for slider in self.sliders:
            vol.append(slider.value())
            slider.update_plasma_timestamp()
        self.sink.set_channel_volumes(vol)

    def setMaximum(self, value):
        for slider in self.sliders:
            slider.setMaximum(value)
 
    def wheelEvent(self, event):
        # dont touch the sliders, they will get the new values
        # via the pa-callback
        # else we get infinite loops
        self.sink.on_step_volume(event.delta() > 0)

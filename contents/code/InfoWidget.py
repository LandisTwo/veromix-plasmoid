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

class SinkInfoWidget(Plasma.TabBar):

    def __init__(self, veromix, sink):
        QGraphicsWidget.__init__(self)
        self.veromix = veromix
        self.sink = sink
        self.text = ""
        self.textwidget = None
        self.INFO_ICON = "hwinfo"
        self.sliders = []
        self.init()

    def init(self):
        self.textwidget = Plasma.TextBrowser()
        self.textwidget.setText("<b>Info</b>")
        self.init_arrangement()
        self.create_text_area()
        self.create_switcher()
        self.create_channel_sliders()
        self.compose_arrangement()

    def compose_arrangement(self):
        self.settings_layout.addItem(self.switcher)
        self.settings_layout.addStretch()
        self.settings_layout.addItem(self.button)
        #self.layout.addItem(self.settings_widget)
        #self.layout.addItem(self.slider_widget)
        self.addTab("Pan", self.slider_widget)
        self.addTab("Settings", self.settings_widget)
        self.addTab("Info", self.textwidget)

    def init_arrangement(self):
        #self.layout = QGraphicsLinearLayout(Qt.Vertical)
        #self.layout.setContentsMargins(42,0,42,0)
        self.layout().setContentsMargins(42,0,42,0)

        self.settings_layout = QGraphicsLinearLayout(Qt.Horizontal)
        self.settings_layout.setContentsMargins(0,0,0,0)

        self.settings_widget = QGraphicsWidget()
        self.settings_widget.setLayout(self.settings_layout)

        #self.setLayout(self.layout)

    def create_channel_sliders(self):
        self.slider_layout = QGraphicsLinearLayout(Qt.Vertical)
        self.slider_layout.setContentsMargins(0,0,0,0)

        self.slider_widget = QGraphicsWidget()
        self.slider_widget.setLayout(self.slider_layout)
        for channel in self.sink.pa_sink.getChannels():
            slider = LabelSlider()
            slider.setOrientation(Qt.Horizontal)
            slider.setBoldText(channel.getName())
            slider.setValue(channel.getVolume())
            slider.setMaximum(100)
            slider.volumeChanged.connect(self.on_slider_cb)
            self.sliders.append(slider)
            self.slider_layout.addItem(slider)

    def create_text_area(self):
        self.button = Plasma.PushButton()
        self.button.setIcon(KIcon(self.INFO_ICON))
        self.button.clicked.connect(self.on_show_message)

    def create_switcher(self):
        self.switcher = Plasma.CheckBox()
        self.switcher.toggled.connect(self.on_change_switcher)
        self.switcher.setText("Default")
        self.switcher.setMinimumSize(self.switcher.preferredSize())

    def update_with_info(self, info):
        self.text = ""
        values = info.props.keys()
        values.sort()
        for key in values:
            self.text += "<b>" + key + ":</b> "+ info.props[key]+"<br/>"
        if self.textwidget:
            self.textwidget.setText(self.text)
        self.set_slider_values()
        self.updateOutputSwitcher()

    def on_change_switcher(self,boolean):
        if boolean:
            self.sink.pa.set_default_sink(self.sink.index )

    def updateOutputSwitcher(self):
        self.switcher.nativeWidget().setChecked(self.sink.pa_sink.props["isdefault"] == "True")

    def on_show_message(self):
        pass
        #if self.veromix.applet.isPopupShowing():
            #self.veromix.applet.hidePopup()
        #self.veromix.showMessage(KIcon(self.INFO_ICON), self.text)

    def set_slider_values(self):
        channels = self.sink.pa_sink.getChannels()
        for i in range(0,len(channels)):
            name = channels[i].getName()
            if name != "None":
                self.sliders[i].setBoldText(name)
            self.sliders[i].setValueFromPulse(channels[i].getVolume())

    def on_slider_cb(self, value):
        vol = []
        for slider in self.sliders:
            vol.append(slider.value())
        self.sink.pa.set_sink_volume(self.sink.index, vol)




class SinkInputInfoWidget(SinkInfoWidget):

    def __init__(self, veromix, sink):
        self.kill_text = "Terminate this sink"
        self.veromix = veromix
        self.sink = sink
        SinkInfoWidget.__init__(self, veromix, sink)
        self.veromix.sinkOutputChanged.connect(self.updateOutputSwitcher)

    def compose_arrangement(self):
        self.settings_layout.addStretch()
        self.settings_layout.addItem(self.switcher)
        self.settings_layout.addItem(self.button)
        #self.layout.addItem(self.settings_widget)
        #self.layout.addItem(self.slider_widget)
        self.addTab("Pan", self.slider_widget)
        self.addTab("Settings", self.settings_widget)
        self.addTab("Info", self.textwidget)

    def create_switcher(self):
        self.switcher = Plasma.ComboBox()
        self.switcher.activated.connect(self.on_change_switcher)

    def keys_for_string(self,  string, values, props):
        text = ""
        rem = []
        for key in values:
            if key.startswith(string):
                k =  key.replace(string, "").lstrip(".").replace(".", " ")
                text += "<b>" + k + ":</b> "+ props[key] +"<br/>"
                rem.append(key)
        for x in rem:
            del values[values.index(x)]
        return text

    def updateOutputSwitcher(self):
        if self.switcher :
            pass
        else:
            return 0
        self.switcher.clear()
        outputs =  self.veromix.get_sinkoutput_widgets()
        ## fill combobox
        for output in outputs:
            self.switcher.addItem(output.app)
        self.switcher.addItem(self.kill_text)
        ## set current selection
        for output in outputs:
            if int(output.index) == int(self.sink.getOutputIndex()) :
                self.switcher.nativeWidget().setCurrentIndex(self.veromix.get_sinkoutput_widgets().index(output))
        self.switcher.setMinimumSize(self.switcher.preferredSize())
        #self.switcher.adjustSize()

    def on_change_switcher(self,event):
        if self.switcher.text() == self.kill_text:
            self.sink.sink_input_kill()
            return 0
        # search ouputs for text, and move sink_input
        for output in self.veromix.get_sinkoutput_widgets():
            if self.switcher.text() == output.app:
                self.sink.pa.move_sink_input(self.sink.index, int(output.index))
                return 0

    def on_slider_cb(self, value):
        vol = []
        for slider in self.sliders:
            vol.append(slider.value())
        self.sink.pa.set_sink_input_volume(self.sink.index, vol)

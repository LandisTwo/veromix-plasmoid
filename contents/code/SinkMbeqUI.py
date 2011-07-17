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

import signal, os, datetime

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyKDE4.kdeui import *
from PyKDE4.plasma import Plasma

from SinkUI import SinkUI
from LabelSlider import *
from SettingsWidget import SinkSettingsWidget

class SinkMbeqUI(SinkUI):
    muteInfo = pyqtSignal(bool)

    def __init__(self , parent):
        self.automatically_muted = False
        self.extended_panel = None
        self.sliders = {}
        self.number_of_siders = 15
        self.ladspa_sink_update = datetime.datetime.now()
        self.ladspa_values = None
        self.ladspa_timer_running = False
        self.module_info = None
        SinkUI.__init__(self, parent)
        self.setContentsMargins(0,0,0,0)

    def initArrangement(self):
        SinkUI.initArrangement(self)
        self.create_sliders()

    def update_label(self):
        text = ""
        try:
            # FIXME
            text = self.name() #self.pa_sink.props["device_name"]
        except:
            pass
        if self.slider:
            self.slider.setBoldText(text)
            self.set_name(self.name())

    def create_settings_widget(self):
        self.settings_widget = SinkSettingsWidget(self.veromix, self)
        self.settings_widget.update_with_info(self.pa_sink)

    def create_sliders(self):
        self.equalizer_widget = QGraphicsWidget()
        self.equalizer_layout = QGraphicsLinearLayout(Qt.Horizontal)
        self.equalizer_layout.setContentsMargins(0,0,0,0)
        self.equalizer_widget.setLayout(self.equalizer_layout)
        self.equalizer_layout.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum))
        for i in range(0,self.number_of_siders):
            self.sliders[i] = LabelSlider()
            self.sliders[i].setMinimum(-70)
            self.sliders[i].setMaximum(30)
            self.sliders[i].setOrientation(Qt.Vertical)
            self.sliders[i].volumeChanged.connect(self.on_sliders_cb)
            self.equalizer_layout.addItem(self.sliders[i])
            self.equalizer_layout.addStretch()

    def composeArrangement(self):
        self.middle_layout.addItem(self.equalizer_widget)
        self.layout.addItem(self.frame)
        self.frame_layout.addItem(self.panel)
        self.panel_layout.addItem(self.mute)
        self.panel_layout.addItem(self.middle)
        self.show_meter = False

    def createMiddle(self):
        self.middle = QGraphicsWidget()
        self.middle_layout = QGraphicsLinearLayout(Qt.Vertical)
        #self.middle_layout.setContentsMargins(6,8,6,0)
        self.middle_layout.setContentsMargins(0,0,0,0)
        self.middle.setLayout(self.middle_layout)
        self.middle.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.createSlider()
        #self.middle_layout.addItem(self.slider)

    def update_module_info(self, index, name, argument, n_used, auto_unload):
        self.module_info = self.parse_module_info(argument)

        self.set_name(self.module_info["sink_name"])
        start = argument.find("control=") + 8
        if start:
            val = argument[start:]
            args=val.split(',')
            for i in range(0,self.number_of_siders):
                self.sliders[i].setValueFromPulse(int(args[i]))

    def parse_module_info(self, string):
        args = {}
        for entry in string.split(" "):
            s = entry.split("=")
            if len(s) == 2:
                args[s[0]]=s[1]
        return args

    def on_sliders_cb(self, value):
        values = []
        for i in range(0,self.number_of_siders):
            values.append(self.sliders[i].value())
            self.sliders[i].update_plasma_timestamp()
        self._schedule_set_ladspa_sink(values)

    def _schedule_set_ladspa_sink(self, value = 0):
        # FIXME
        now = datetime.datetime.now()
        if value == 0:  # case timer-callback
            self.ladspa_timer_running = False
        else:
            self.ladspa_values = value
            self.ladspa_sink_update = now
        time =  (now - self.ladspa_sink_update).microseconds
        if time > 500000 and not self.ladspa_timer_running:
            # FIXME
            self._set_ladspa_sink(self.ladspa_values)
            self.ladspa_sink_update = now
        else:
            if not self.ladspa_timer_running:
                self.ladspa_timer_running = True
                QTimer.singleShot(500, self._schedule_set_ladspa_sink)

    def _set_ladspa_sink(self, values):
        if self.module_info == None:
            return
        control = ""
        for val in values:
            control = control +  str(val) + ","
        self.module_info["control"] = control[:-1]
        parameters = "sink_name=%(sink_name)s master=%(master)s plugin=%(plugin)s  label=%(label)s control=%(control)s" % self.module_info
        self.pa_sink.set_ladspa_sink(parameters)

    def on_expander_clicked(self):
        self.pa_sink.remove_ladspa_sink()

    def create_expander(self):
        SinkUI.create_expander(self)
        self.expander.setSvg("widgets/configuration-icons", "close")

    def get_ladspa_type(self):
        return "mbeq_1197"

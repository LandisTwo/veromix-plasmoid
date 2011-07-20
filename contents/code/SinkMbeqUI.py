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
        self.timer = QTimer()
        self.timer.timeout.connect(self.on_timer)
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
            self.set_name(text)

    def create_settings_widget(self):
        self.settings_widget = SinkSettingsWidget(self.veromix, self)
        self.settings_widget.update_with_info(self.pa_sink)

    effects = { "dj_eq_mono" : {"plugin": "dj_eq_1901",
                               "control": "0,0,0",
                               "range" : [[-70, 6],[-70, 6],[-70, 6]] },
                "flanger" :    {"plugin": "flanger_1191",
                               "control": "0,0,0",
                               "range" : [[0.1, 25],[0, 10],[0, 100],[-1, 1]] },
                "multivoiceChorus" :    {"plugin": "multivoice_chorus_1201",
                               "control": "0,0,0,0,0,0",
                               "range" : [[1, 8], [10, 40], [0, 2], [0, 5], [2, 30], [-20, 0]] }}
        ## GOOD
        #sink_name="sink_name=ladspa_output.dj_eq_1901.dj_eq."+str(self.ladspa_index)
        #plugin = "plugin=dj_eq_1901"
        #label = "label=dj_eq_mono"
        #control = "control=0,0,0"

        ##works but ..
        #sink_name="sink_name=ladspa_output.flanger_1191.flanger."+str(self.ladspa_index)
        #plugin = "plugin=flanger_1191"
        #label = "label=flanger"
        #control = "control=0,0,0,0"

        ## fun!
        #sink_name="sink_name=ladspa_output.multivoice_chorus_1201.multivoiceChorus."+str(self.ladspa_index)
        #plugin = "plugin=multivoice_chorus_1201"
        #label = "label=multivoiceChorus"
        #control = "control=0,0,0,0,0,0"

        ## fun
        #sink_name="sink_name=ladspa_output.pitch_scale_1193.pitchScale."+str(self.ladspa_index)
        #plugin = "plugin=pitch_scale_1193"
        #label = "label=pitchScale"
        #control = "control=1.9"



    def create_sliders(self):
        self.sliders = {}
        self.equalizer_widget = QGraphicsWidget()
        self.equalizer_layout = QGraphicsLinearLayout(Qt.Horizontal)
        self.equalizer_layout.setContentsMargins(0,0,0,0)
        self.equalizer_widget.setLayout(self.equalizer_layout)
        self.equalizer_layout.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum))
        if self.module_info == None:
            return
        for i in range(0,self.number_of_siders):
            self.sliders[i] = LabelSlider()
            label = self.module_info["label"]
            if label  in self.effects.keys():
                val = self.effects[label]
                self.sliders[i].setMinimum(val["range"][i][0])
                self.sliders[i].setMaximum(val["range"][i][1])
            else:
                self.sliders[i].setMinimum(-70)
                self.sliders[i].setMaximum(30)
            self.sliders[i].setOrientation(Qt.Vertical)

            self.sliders[i].volumeChanged.connect(self.on_sliders_cb)
            self.equalizer_layout.addItem(self.sliders[i])
            self.equalizer_layout.addStretch()

    def remove_equalizer_widget(self):
        self.middle_layout.removeItem(self.equalizer_widget)

    def add_equalizer_widget(self):
        self.middle_layout.addItem(self.equalizer_widget)

    def composeArrangement(self):
        self.add_equalizer_widget()
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
        controls = self.module_info["control"].split(",")
        count = len(controls)
        if count != self.number_of_siders:
            self.number_of_siders = count
            self.remove_equalizer_widget()
            self.create_sliders()
            self.add_equalizer_widget()
        self.set_name(self.module_info["sink_name"])
        for i in range(0,self.number_of_siders):
            self.sliders[i].setValueFromPulse(int(controls[i]))

    def parse_module_info(self, string):
        args = {}
        controls = string.split(" ")
        for entry in controls:
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

    def on_timer(self):
        self.timer.stop()
        self._set_ladspa_sink(self.ladspa_values)

    def _schedule_set_ladspa_sink(self,values):
        if self.timer.isActive():
            self.timer.stop()
        self.ladspa_values = values
        self.timer.start(1000)

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
        # FIXME
        return "ladspa"

    def wheelEvent(self, event):
        pass

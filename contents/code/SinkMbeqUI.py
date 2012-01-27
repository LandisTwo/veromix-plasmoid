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
from LADSPAEffects import *

class SinkMbeqUI(SinkUI):
    muteInfo = pyqtSignal(bool)

    def __init__(self , parent):
        self.effects = LADSPAEffects.effects
        self.automatically_muted = False
        self.extended_panel = None
        self.sliders = {}
        self.number_of_siders = 0
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
        self.create_header()

    def update_label(self):
        text = ""
        try:
            # FIXME
            text = self.pa_sink.props["device.ladspa.name"] #self.name() #self.pa_sink.props["device_name"]
        except:
            pass
        if self.slider:
            self.label.setBoldText(text)
            self.set_name(text)

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
            self.sliders[i] = VerticalSlider()
            self.sliders[i].setOrientation(Qt.Vertical)
            self.sliders[i].nativeWidget().actionTriggered.connect(self.on_sliders_cb)
            self.equalizer_layout.addItem(self.sliders[i])
            self.equalizer_layout.addStretch()

    def remove_equalizer_widget(self):
        self.middle_layout.removeItem(self.equalizer_widget)

    def add_equalizer_widget(self):
        self.middle_layout.addItem(self.equalizer_widget)

    def composeArrangement(self):
        self.middle_layout.addItem(self.header_widget)
        self.add_equalizer_widget()
        self.layout.addItem(self.frame)
        self.frame_layout.addItem(self.panel)
        self.panel_layout.addItem(self.mute)
        self.panel_layout.addItem(self.middle)
        self.show_meter = False

    def create_header(self):
        self.header_widget = QGraphicsWidget()
        self.header_layout = QGraphicsLinearLayout(Qt.Horizontal)
        #self.header_layout.setContentsMargins(6,8,6,0)
        self.header_layout.setContentsMargins(0,0,12,0)
        self.header_widget.setLayout(self.header_layout)
        self.header_widget.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.label = Label()
        self.label.setContentsMargins(0,0,0,0)
        self.label.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed))
        self.header_layout.addItem(self.label)

    def _get_effect_settings(self):
         label = self.module_info["label"]
         return self.effects[label]

    def on_change_effect(self, value):
        for key in self.effects.keys():
            if self.effects[key]["name"] == value:
                #"sink_name=ladspa_output.dj_eq_1901.dj_eq."+str(self.ladspa_index)
                parameters = "sink_name=ladspa_output."+self.effects[key]["plugin"]+"."+key
                parameters =  parameters + " master=%(master)s " % self.module_info
                parameters =  parameters + " plugin=" + self.effects[key]["plugin"]
                parameters =  parameters + " label=" + key
                parameters =  parameters + " control=" + self.effects[key]["control"]
                self.pa_sink.set_ladspa_sink(parameters)

    def createMiddle(self):
        self.middle = QGraphicsWidget()
        self.middle_layout = QGraphicsLinearLayout(Qt.Vertical)
        #self.middle_layout.setContentsMargins(6,8,6,0)
        self.middle_layout.setContentsMargins(0,0,0,0)
        self.middle.setLayout(self.middle_layout)
        self.middle.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.createSlider()
        #self.middle_layout.addItem(self.slider)

    def context_menu_create_custom(self):
        self.create_menu_switch_effect()
        self.action_kill = QAction(i18n("Disconnect/kill"), self.popup_menu)
        self.popup_menu.addAction(self.action_kill)
        self.action_kill.triggered.connect(self.on_menu_kill_clicked)

    def create_menu_switch_effect(self):
        effect_menu = QMenu(i18n("Effect"), self.popup_menu)
        sinks = self.veromix.get_sink_widgets()
        for key in self.effects.keys():
            effect = self.effects[key]
            action = QAction(effect["name"],effect_menu)
            effect_menu.addAction(action)
            if self.module_info["label"] == key:
                action.setCheckable(True)
                action.setChecked(True)
                action.setEnabled(False)
        self.popup_menu.addMenu(effect_menu)

    def on_contextmenu_clicked(self, action):
        self.on_change_effect(action.text())

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
            effect = self._get_effect_settings()
            scale = effect["scale"][i]
            minmax = effect["range"][i]
            self.sliders[i].setMinimum(minmax[0] * scale)
            self.sliders[i].setMaximum(minmax[1] * scale, False)
            self.sliders[i].setText(effect["labels"][i])
            #self.sliders[i].setBoldText(str(controls[i]))

            tooltip = Plasma.ToolTipContent()
            #tooltip.setImage(pixmapFromSVG("audio-volume-high"))
            tooltip.setMainText(effect["name"] + " - " + effect["labels"][i] )
            tooltip.setSubText(controls[i])
            Plasma.ToolTipManager.self().setContent(self.sliders[i], tooltip)
            Plasma.ToolTipManager.self().registerWidget(self.sliders[i])

            value = float(controls[i]) * scale
            self.sliders[i].setValue(int(value))

    def parse_module_info(self, string):
        args = {}
        controls = string.split(" ")
        for entry in controls:
            s = entry.split("=")
            if len(s) == 2:
                args[s[0]]=s[1]
        return args

    def on_sliders_cb(self, action):
        if action == 7 or action == 3:
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
        effect = self.effects[self.module_info["label"]]
        i = 0
        for val in values:
            scale = effect["scale"][i]
            control = control +  str(float(val)/float(scale)) + ","
            i = i + 1
        self.module_info["control"] = control[:-1]
        parameters = "sink_name=%(sink_name)s master=%(master)s plugin=%(plugin)s  label=%(label)s control=%(control)s" % self.module_info
        self.pa_sink.set_ladspa_sink(parameters)

    def on_menu_kill_clicked(self):
        self.pa_sink.remove_ladspa_sink()

    def get_ladspa_type(self):
        # FIXME
        return "ladspa"

    def wheelEvent(self, event):
        pass

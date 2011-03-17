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
from PyKDE4.kdecore import *
from PyQt4.QtGui import *
from PyKDE4.kdeui import *

        
class SinkSettingsWidget(QGraphicsWidget):

    def __init__(self, veromix, sink):
        QGraphicsWidget.__init__(self)
        self.veromix = veromix
        self.sink = sink
        self.init()

    def init(self):
        self.init_arrangement()
        self.create_switcher()
        self.create_profile_switcher()
        self.compose_arrangement()
        
    def compose_arrangement(self):

        self.switcher.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.profile_switcher.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed))
        self.layout.addItem(self.switcher)
        self.layout.addItem(self.profile_switcher)

    def init_arrangement(self):
        self.layout = QGraphicsLinearLayout(Qt.Horizontal)
        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)
        #self.layout().setContentsMargins(42,0,42,0)        
        #self.settings_layout = QGraphicsLinearLayout(Qt.Horizontal)
        #self.settings_layout.setContentsMargins(0,0,0,0)        
        #self.settings_widget = QGraphicsWidget()
        #self.settings_widget.setLayout(self.settings_layout)
        
    def create_switcher(self):
        self.switcher = Plasma.CheckBox()
        self.switcher.toggled.connect(self.on_change_switcher)
        self.switcher.setText(i18n("Default Sink"))
        self.switcher.setMinimumSize(self.switcher.preferredSize())

    def create_profile_switcher(self):
        self.profile_switcher = Plasma.ComboBox()
        self.profile_switcher.activated.connect(self.on_change_profile)

    def update_with_info(self, info):
        self.updateOutputSwitcher()        

    def on_change_profile(self,value):
        print "profile changed", value

    def on_change_switcher(self,boolean):
        if boolean:
            self.sink.pa.set_default_sink(self.sink.index )

    def updateOutputSwitcher(self):
        if self.sink.pa_sink:
            self.switcher.nativeWidget().setChecked(self.sink.pa_sink.props["isdefault"] == "True")
        if self.veromix:
            info = self.veromix.get_card_info_for(self.sink)
            if info:
                self.profile_switcher.clear()
                profiles = info.get_profiles()
                active = info.get_active_profile_name()
                active_index = 0
                for profile in profiles:
                    self.profile_switcher.addItem(profile.description)
                    if active == profile.name:
                        active_index = profiles.index(profile)
                self.profile_switcher.nativeWidget().setCurrentIndex(active_index)


                
class SinkInputSettingsWidget(SinkSettingsWidget):

    def __init__(self, veromix, sink):
        self.kill_text = i18n("Disconnect/kill")
        SinkSettingsWidget.__init__(self, veromix, sink)
        self.veromix.sinkOutputChanged.connect(self.updateOutputSwitcher)

    def init(self):
        self.init_arrangement()
        self.create_switcher()
        self.compose_arrangement()

    def compose_arrangement(self):
        #self.layout.addStretch()
        self.layout.addItem(self.label)
        self.layout.addItem(self.switcher)

    def create_switcher(self):
        self.label = Plasma.Label()
        #self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed,True) )
        self.label.setText(i18n("Output"))
        self.switcher = Plasma.ComboBox()
        self.switcher.activated.connect(self.on_change_switcher)

    def updateOutputSwitcher(self):
        if self.switcher == None or self.sink.pa_sink == None:
             return 0
        self.switcher.clear()
        outputs =  self.veromix.getSinkOutputs()
            
        for output in outputs:
            self.switcher.addItem(output.app)
        self.switcher.addItem(self.kill_text)
        ## set current selection
        for output in outputs:
            if int(output.index) == int(self.sink.getOutputIndex()) :
                self.switcher.nativeWidget().setCurrentIndex(self.veromix.getSinkOutputs().index(output))
        self.switcher.setMinimumSize(self.switcher.preferredSize())

    def on_change_switcher(self,event):
        if self.switcher.text() == self.kill_text:
            self.sink.sink_input_kill()
            return 0
        # search ouputs for text, and move sink_input
        for output in self.veromix.getSinkOutputs():
            if self.switcher.text() == output.app:
                self.sink.pa.move_sink_input(self.sink.index, int(output.index))
                return 0


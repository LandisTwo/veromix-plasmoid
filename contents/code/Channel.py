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

import   datetime
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyKDE4.kdeui import *
from PyKDE4.plasma import Plasma

from LabelSlider import LabelSlider
from InfoWidget import SinkInfoWidget
from MuteButton  import MuteButton
from ClickableMeter import ClickableMeter

class Channel( Plasma.Frame):
    def __init__(self , parent):
        Plasma.Frame.__init__(self)
        self.setFrameShadow(Plasma.Frame.Sunken)
        self.veromix = parent
        self.index = -1
        self.pa = parent.getPulseAudio()
        self.app = "output"   # str(sink.client_id )
        self.name = "" #sink.name
        self.sortOrderIndex = 0
        self.deleted = True
        self.pa_sink = None
        d =  datetime.timedelta(seconds=2)
        self.pulse_timestamp = datetime.datetime.now()  + d
        self.plasma_timestamp = datetime.datetime.now() + d

        self.extended_panel_shown = False
        self.setFrameShadow(Plasma.Frame.Sunken)
        self.init()

    def init(self):
        self.layout = QGraphicsLinearLayout(Qt.Vertical)
        # padding:
        self.layout.setContentsMargins(6,3,6,3)
        #self.layout.setContentsMargins(6,6,6,6)
        self.setLayout(self.layout)
        self.initArrangement()
        self.composeArrangement()
        self.setAcceptDrops(True)
        self.on_show_info_widget()
        self.on_show_info_widget()

    def initArrangement(self):
        self.createExtender()
        self.createPanel()
        self.createMute()
        self.createMiddle()
        self.createMeter()

    def composeArrangement(self):
        self.layout.addItem(self.panel)
        self.panel_layout.addItem(self.meter)
        self.panel_layout.addItem(self.middle)
        self.panel_layout.addItem(self.mute)

    def createExtender(self):
        self.extended_panel = SinkInfoWidget(self.veromix, self )

    def createPanel(self):
        self.panel = QGraphicsWidget()
        self.panel_layout = QGraphicsLinearLayout(Qt.Horizontal)
        self.panel_layout.setContentsMargins(0,0,0,0)
        self.panel.setLayout(self.panel_layout)

    def createMute(self):
        self.mute = MuteButton(self)
        self.mute.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum,True) )
        self.connect(self.mute, SIGNAL("clicked()"), self.on_mute_cb  )

    def createMiddle(self):
        self.middle = QGraphicsWidget()
        self.middle_layout = QGraphicsLinearLayout(Qt.Vertical)
        self.middle_layout.setContentsMargins(6,8,6,0)

        self.middle.setLayout(self.middle_layout)
        self.middle.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.createSlider()
        self.connect(self.slider, SIGNAL("valueChanged(int)"), self.on_slider_cb  )
        self.middle_layout.addItem(self.slider)

    def createSlider(self):
        self.slider = LabelSlider()
        self.slider.setOrientation(Qt.Horizontal)
        self.slider.setMaximum(100)
        self.slider.setMinimum(0)

    def createMeter(self):
        self.meter = ClickableMeter()
        self.meter.setMeterType(Plasma.Meter.AnalogMeter)
        self.meter.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum, True))
        self.connect(self.meter, SIGNAL("clicked()"), self.on_show_info_widget  )

    def update_pulse_timestamp(self):
        self.pulse_timestamp = datetime.datetime.now()

    def update_plasma_timestamp(self):
        self.plasma_timestamp = datetime.datetime.now()

    def _set_values(self, info):
        self.updateIcon()
        self.update_label()

    def on_show_info_widget(self):
        pass

    def on_mute_cb(self ):
        pass

    def on_update_meter(self, index, value, number_of_sinks):
        pass

    def update_essentials(self,info):
        self.name = info.name
        self.pa_sink = info
        self.index = info.index
        self.updateSortOrderIndex()

    def update_with_info(self,info):
        self.update_essentials(info)
        now = datetime.datetime.now()
        if (now - self.plasma_timestamp).seconds > 1 :
            self.update_pulse_timestamp()
            self.slider.setValue(info.getVolume())
        self._set_values(info)
        self.update()
        if self.extended_panel:
            self.extended_panel.update_with_info(info)

    def updateSortOrderIndex(self):
        self.sortOrderIndex =  self.sinkIndexFor(self.index)

    def update_label(self):
        pass

    #
    def sinkIndexFor( self, index ):
        return (index * 100000) + 100000

    def updateIcon(self):
        pass

    def on_slider_cb(self, value):
        now = datetime.datetime.now()
        if (now - self.pulse_timestamp ).seconds > 1:
            self.update_plasma_timestamp()
            self.setVolume(value)

    def isSourceOutput(self):
        return False

    def isDefaultSink(self):
        return False

    def startDrag(self,event):
        pass

    def removeSlider(self):
        # if a slider is not visible, plasmoidviewer crashes if the slider is not removed.. (dont ask me)
        self.middle_layout.removeItem(self.slider)
        self.slider = None

    def isSinkOutput(self):
        return False

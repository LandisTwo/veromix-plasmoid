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

class Channel(QGraphicsWidget):
    def __init__(self , parent):
        QGraphicsWidget.__init__(self)
        self.veromix = parent
        self.index = -1
        self.pa = parent.getPulseAudio()
        self.app = "output"  
        self.name = "" 
        self.sortOrderIndex = 0
        self.deleted = True
        self.pa_sink = None
        self.extended_panel_shown = False
        self.extended_panel= None
        self.init()

    def init(self):
        self.layout = QGraphicsLinearLayout(Qt.Vertical)
        self.layout.setContentsMargins(2,2,2,2)
        self.setLayout(self.layout)
        self.initArrangement()
        self.composeArrangement()
        self.setAcceptDrops(True)

    def initArrangement(self):
        self.create_frame()
        self.create_panel()
        self.createMute()
        self.createMiddle()
        self.createMeter()

    def composeArrangement(self):
        self.layout.addItem(self.frame)
        self.frame_layout.addItem(self.panel)
        
        self.panel_layout.addItem(self.mute)
        self.panel_layout.addItem(self.middle)
        self.panel_layout.addItem(self.meter)

    def createExtender(self):
        self.extended_panel = SinkInfoWidget(self.veromix, self )

    def create_frame(self):
        self.frame = Plasma.Frame()
        self.frame_layout = QGraphicsLinearLayout(Qt.Vertical)
        self.frame.setEnabledBorders (Plasma.FrameSvg.NoBorder)
        self.frame.setFrameShadow(Plasma.Frame.Plain)
        self.frame_layout.setContentsMargins(0,0,0,0)
        self.frame.setLayout(self.frame_layout)

    def create_panel(self):
        self.panel = QGraphicsWidget()
        self.panel_layout = QGraphicsLinearLayout(Qt.Horizontal)
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
        self.slider.volumeChanged.connect( self.on_slider_cb  )
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
        self.slider.setValueFromPulse(info.getVolume())
        self._set_values(info)
        self.update()
        if self.extended_panel:
            self.extended_panel.update_with_info(info)

    def updateSortOrderIndex(self):
        self.sortOrderIndex =  self.sinkIndexFor(self.index)

    def update_label(self):
        pass

    def sinkIndexFor( self, index ):
        return (index * 100000) + 100000

    def updateIcon(self):
        pass

    def on_slider_cb(self, value):
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

    def isSinkInput(self):
        return False

    def isNowplaying(self):
        return False

    def setVolume(self, value):
        pass

    def setVolumes(self, values):
        pass
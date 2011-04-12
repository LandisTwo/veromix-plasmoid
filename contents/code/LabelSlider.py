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

import datetime
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyKDE4.plasma import Plasma
from PyKDE4 import plasmascript
from PyKDE4.kdeui import *
from PyKDE4.kdecore import *
from PyKDE4.kdecore import *
from PyKDE4.plasma import *

class Label(Plasma.Label):
    volumeChanged = pyqtSignal(int)
    
    def __init__(self, parent=None):
        self.text = ""
        self.bold_text = ""
        Plasma.Label.__init__(self, parent)

    def setText(self, text):
        if text and text != "None":
            self.text = text
        self._set_text()

    def setBoldText(self,text):
        if text and text != "None":
            self.bold_text = text
        self._set_text()

    def _set_text(self):
        Plasma.Label.setText(self, "<b>"+self.bold_text+"</b> "+self.text)

    def setMinimum(self, value):
        pass

    def setMaximum(self, value):
        pass
    
class LabelSlider(Plasma.Slider):
    volumeChanged = pyqtSignal(int)
    
    def __init__(self):
        self.DELAY=  1
        self.text = ""
        self.bold_text = ""
        d =  datetime.timedelta(seconds=2)
        self.pulse_timestamp = datetime.datetime.now()  + d
        self.plasma_timestamp = datetime.datetime.now() + d
        Plasma.Slider.__init__(self)
        self.label = Label(self)
        self.label.setPos(0, -4)

        self.connect(self, SIGNAL("geometryChanged()"), self._resize_widgets)
        self.valueChanged.connect( self.on_slider_cb)

    def setMaximum(self, value):
        Plasma.Slider.setMaximum(self,value)
        if value > 100:
            self.nativeWidget().setTickInterval(100)
            self.nativeWidget().setTickPosition(QSlider.TicksBothSides)
        else:
            self.nativeWidget().setTickPosition(QSlider.NoTicks)
            
    def _resize_widgets(self):
        w = self.size().width() 
        self.label.setMinimumWidth(w)
        self.label.setMaximumWidth(w)
        
    def setText(self, text):
        self.label.setText(text)
        
    def setBoldText(self,text):
        self.label.setBoldText(text)
    
    def setValueFromPlasma(self, value):
        if self.check_pulse_timestamp():
            self.update_plasma_timestamp()
            self.setValue(value)

    def update_with_info(self, info):
        self.setValueFromPulse(info.getVolume())
        
    def setValueFromPulse(self, value):
        if self.check_plasma_timestamp():
            self.update_pulse_timestamp()
            self.setValue(value)

    def on_slider_cb(self, value):
        if self.check_pulse_timestamp():
            self.update_plasma_timestamp()
            self.volumeChanged.emit(value)

# private
    def update_pulse_timestamp(self):
        self.pulse_timestamp = datetime.datetime.now()

    def update_plasma_timestamp(self):
        self.plasma_timestamp = datetime.datetime.now()

## testing
    def check_plasma_timestamp(self):
        now = datetime.datetime.now()
        return  (now - self.plasma_timestamp ).seconds > self.DELAY
        
    def check_pulse_timestamp(self):
        now = datetime.datetime.now()
        return  (now - self.pulse_timestamp ).seconds > self.DELAY

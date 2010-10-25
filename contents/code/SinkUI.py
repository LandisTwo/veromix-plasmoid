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

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyKDE4.kdeui import *
from PyKDE4.plasma import Plasma

import signal, os, datetime
from LabelSlider import *
from InfoWidget import *
from MuteButton  import *
from ClickableMeter import *
from Channel import *

class SinkUI(Channel):
    muteInfo = pyqtSignal(bool)
    
    def __init__(self , parent):
        self.meter_levels = {} 
        self.number_of_input_sinks = 0
        Channel.__init__(self, parent)
               
    def updateIcon(self):           
        if self.isMuted():
            self.updateMutedInfo(True)
            self.mute.setMuted(True)
        else:
            self.updateMutedInfo(self.pa_sink.getVolume() <= 1 )
            self.mute.setMuted(False)

    def updateMutedInfo(self, aBoolean):
        if self.isDefaultSink():
            self.muteInfo.emit(aBoolean)

    def on_update_meter(self, index, value, number_of_sinks):
        if (self.number_of_input_sinks != number_of_sinks):
            self.number_of_input_sinks = number_of_sinks
            self.meter_levels[index] = {}
        self.meter_levels[index] = value
        
        level = 0
        for i in self.meter_levels:
            if self.meter_levels[i] > level:
                level = self.meter_levels[i]

        vol = self.pa_sink.getVolume()
        level =   level * (vol / 100.0)
        self.meter.setValue(level)

    def isMuted(self):
        return self.pa_sink.mute == 1       
    
    def on_mute_cb(self ):
        if self.isMuted():
            self.pa.set_sink_mute(self.index, False)
        else:
            self.pa.set_sink_mute(self.index, True)

    def on_slider_cb(self, value):
        now = datetime.datetime.now()
        if (now - self.pulse_timestamp ).seconds > 1:
            self.update_plasma_timestamp()
            self.setVolume(value)

    def isDefaultSink(self):
        return self.pa_sink.props["isdefault"] == "True"

    def on_step_volume(self, up):
        vol = self.pa_sink.getVolume()
        STEP = 5
        if up:
            vol = vol + STEP
        else:
            vol = vol - STEP
        if vol < 0:
            vol = 0
        if vol > 100:
            vol = 100
        self.setVolume(vol)

    def on_show_info_widget(self):
        if (self.extended_panel_shown):
            self.extended_panel_shown = False
            self.extended_panel.hide()
            self.layout.removeItem( self.extended_panel)
        else:
            self.extended_panel_shown = True
            self.layout.insertItem(0, self.extended_panel)
            self.extended_panel.show()
        self.adjustSize()
        self.veromix.check_geometries()

    def setVolume(self, value):        
        self.pa.set_sink_volume(self.index, value)

    def sink_input_kill(self):
        pass

    def update_label(self):
        text = ""
        try:
            self.app = self.pa_sink.props["device_name"]
        except:
            pass
        if self.slider:
            self.slider.setBoldText(self.app)

## Drag and Drop Support

    def dropEvent(self, dropEvent):
        uris = dropEvent.mimeData().urls()
        for uri in uris:
            if uri.scheme() == "veromix":
                self.pa.move_sink_input(uri.port(), self.index)

    def startDrag(self,event):          
         pass
    
                
    def paint2(self, painter,  option, widget = 0):
        QGraphicsWidget.paint(self, painter, option, widget)
        margin = 10
        width = 6
        height = 6
        size = self.contentsRect()
        
        m_left = margin 
        m_right =  size.width() - ( margin) - width  
        m_top = margin 
        m_bottom = size.height()  -  ( margin) - height
        
        print m_left, m_top, m_right, m_bottom
        painter.setRenderHint(QPainter.Antialiasing)
        #p = Plasma.PaintUtils.roundedRectangle(
                            #self.contentsRect().adjusted(m_left, m_top, -m_right, -m_bottom), 4)
        p = Plasma.PaintUtils.roundedRectangle(
                            self.contentsRect().adjusted(m_left, m_top, -m_right, -m_bottom), 4)
        c = Plasma.Theme.defaultTheme().color(Plasma.Theme.TextColor)
        c.setAlphaF(0.3)
        painter.fillPath(p, c)
                
    def isSinkOutput(self):
        return True


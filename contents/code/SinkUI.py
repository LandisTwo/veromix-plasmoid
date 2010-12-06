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
from PyKDE4.kdeui import *
from PyKDE4.plasma import Plasma

from Channel import Channel

class SinkUI(Channel):
    muteInfo = pyqtSignal(bool)

    def __init__(self , parent):
        Channel.__init__(self, parent)
        size = 40
        self.setMinimumHeight(s)
        self.setMaximumHeight(s)
        self.setPreferredHeight(s)

    def updateIcon(self):
        if self.isMuted():
            self.updateMutedInfo(True)
            self.mute.setMuted(True)
        else:
            self.updateMutedInfo(False)
            self.mute.setMuted(False)

    def updateMutedInfo(self, aBoolean):
        if self.isDefaultSink():
            self.muteInfo.emit(aBoolean)
    
    def on_update_meter(self, index, value, old):
        level = 0
        for sink in self.veromix.getSinkInputs():
            if sink.getOutputIndex() == str(self.index):
                meter = sink.getMeter()   
                if meter > level:
                    level = meter
        vol = self.getVolume()
        level =   level * (vol / 100.0)
        self.meter.setValue(level)

    def getVolume(self):
        return self.pa_sink.getVolume()

    def getMeter(self):
        return 0

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

    def isSinkOutput(self):
        return True

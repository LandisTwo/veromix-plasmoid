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
        self.automatically_muted = False
        self.extended_panel = None
        Channel.__init__(self, parent)        
        self.setContentsMargins(0,0,0,0)

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
        self.veromix.pa.toggle_monitor_of_sink(self.index, str(self.name) )
        self.meter.setValue(0)

    def setVolume(self, value):
        vol = self.pa_sink.volumeDiffFor(value)
        for c in vol:
            if c <= 0:
                ## FIXME HACK for MurzNN this should be conditional
                self.pa.set_sink_mute(self.index, True)
                self.automatically_muted = True
                return    
        if self.automatically_muted :            
            self.automatically_muted = False
            self.pa.set_sink_mute(self.index, False)
        self.set_channel_volumes(vol)
            
    def set_channel_volumes(self, values):
        self.pa.set_sink_volume(self.index, values)

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

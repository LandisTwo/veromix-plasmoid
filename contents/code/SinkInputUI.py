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
from SinkUI import *
from Channel import *
from MuteButton  import InputMuteButton

class InputSinkUI(SinkUI):

    def __init__(self , parent):
        self.mouse_pressed = False
        SinkUI.__init__(self, parent)
        self.setContentsMargins(0,0,0,0)
        self.frame.setEnabledBorders (Plasma.FrameSvg.NoBorder)
        self.frame.setFrameShadow(Plasma.Frame.Plain)

    def init(self):
        SinkUI.init(self)
        self.setAcceptDrops(False)
        self.layout.setContentsMargins(6,2,6,0)
        self.updateBorders()

    def hasNowPlayingExtension(self):
        for player in self.veromix.getNowPlaying():
            if player.matches(self):
                return True
        return False

    def updateBorders(self):
        pass

    def createMute(self):
        self.mute = InputMuteButton(self)
        self.mute.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum,True) )
        self.connect(self.mute, SIGNAL("clicked()"), self.on_mute_cb  )

    def createExtender(self):
        self.extended_panel = SinkInputInfoWidget(self.veromix, self)

    def setVolume(self, value):
        v = self.pa_sink.volumeDiffFor(value)
        self.pa.set_sink_input_volume(self.index, v)

    def getMeter(self):
        return self.meter.value()

    def on_show_info_widget(self):
        self.veromix.pa.start_monitor_for_sinkinput(self.index, int(self.getOutputIndex()), self.name )
        self.meter.setValue(0)

    def on_mute_cb(self ):
        if self.isMuted():
            self.pa.set_sink_input_mute(self.index, False)
        else:
            self.pa.set_sink_input_mute(self.index, True)

    def sink_input_kill(self):
        self.pa.sink_input_kill(self.index)

    def updateSortOrderIndex(self):
        if self.pa_sink:
            self.sortOrderIndex =  self.sinkIndexFor(int(self.getOutputIndex())) - (self.index * 10 )

    def getOutputIndex(self):
        return self.pa_sink.props["sink"]

    def composeArrangement(self):
        self.layout.addItem(self.frame)
        self.frame_layout.addItem(self.panel)        
        self.panel_layout.addItem(self.mute)
        self.panel_layout.addItem(self.middle)
        self.panel_layout.addItem(self.meter)

    def updateMutedInfo(self, aBoolean):
        pass

    def update_label(self):
        text =  self.pa_sink.name
        bold = self.pa_sink.props["app"]
        if self.slider:
            self.slider.setText(text)
            self.slider.setBoldText(bold)
            self.text = bold
        iconname = None
        if self.pa_sink.props["app_icon"] != "None":
            iconname = self.pa_sink.props["app_icon"]
        if iconname == None and  self.pa_sink.props["app"] != "None":
            iconname = self.veromix.query_application(self.pa_sink.props["app"])
        if iconname is None and bold == "plugin-container":
            iconname = 'flash'
        if iconname :
            self.mute.setBigIconName(iconname)
            self.updateIcon()

    def on_update_meter(self, index, value, number_of_sinks):
        if self.index == index:
            self.meter.setValue(value)

### Drag and Drop

    def mousePressEvent(self, event):
        self.mouse_pressed = True

    def mouseReleaseEvent(self, event):
        self.mouse_pressed = False

    def mouseMoveEvent(self,e):
        if self.mouse_pressed :
            self.startDrag(e)

    def startDrag(self,event):
        drag = QDrag(event.widget())
        mimedata = QMimeData()
        liste = []
        liste.append(QUrl( "veromix://sink_input_index:"+str(int(self.index)) ))
        mimedata.setUrls(liste)
        drag.setMimeData(mimedata)
        #drag.setHotSpot(event.pos() - self.rect().topLeft())
        dropAction = drag.start(Qt.MoveAction)

    def isSinkOutput(self):
        return False

    def isSinkInput(self):
        return True

    def isDefaultSink(self):
        return False

    def update_with_info(self,info):
        SinkUI.update_with_info(self, info)
        self.updateBorders()

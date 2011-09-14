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
from Channel import *
from MuteButton  import *
from ClickableMeter import *

class SourceOutputUI( Channel ):
    def __init__(self , parent):
        self.mouse_pressed = False
        Channel.__init__(self, parent)
        self.layout.setContentsMargins(6,2,6,2)

    def createMute(self):
        self.mute = InputMuteButton(self)
        self.mute.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum,True) )
        self.connect(self.mute, SIGNAL("clicked()"), self.on_mute_cb  )
        self.mute.setBigIconName("audio-input-microphone.png")

    def createSlider(self):
        self.slider = Label()

    def create_expander(self):
        pass

    def update_label(self):
        text =  ""
        bold = self.pa_sink.name
        if "description" in self.pa_sink.props.keys():
            bold = self.pa_sink.props["description"]
            text = self.pa_sink.name

        if self.name().find("ALSA") == 0 and "application.process.binary" in self.pa_sink.props.keys():
            bold = self.pa_sink.props[ "application.process.binary"]
            text =  self.pa_sink.props[ "application.name"]
        self.set_name(bold)

        if self.slider:
            self.slider.setText(text)
            self.slider.setBoldText(bold)
        iconname = None
        if "application.icon_name" in self.pa_sink.props.keys():
            iconname = self.pa_sink.props["application.icon_name"]
        if iconname == None and  "app" in self.pa_sink.props.keys():
            iconname = self.veromix.query_application(self.pa_sink.props["app"])

        if iconname is None and bold == "plugin-container":
            iconname = 'flash'

        if iconname :
            self.mute.setBigIconName(iconname)
            self.updateIcon()

    def get_assotiated_source(self):
        try:
            return self.pa_sink.props["source"]
        except:
            return 0

    def on_slider_cb(self, value):
        pass

    def on_update_meter(self, index, value, number_of_sinks):
        if self.getOutputIndex() == index:
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
        liste.append(QUrl( "veromix://source_output_index:"+str(int(self.index)) ))
        mimedata.setUrls(liste)
        drag.setMimeData(mimedata)
        #drag.setHotSpot(event.pos() - self.rect().topLeft())
        dropAction = drag.start(Qt.MoveAction)


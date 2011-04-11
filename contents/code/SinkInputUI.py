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
from SinkUI import *
from Channel import *
from MuteButton  import InputMuteButton
from SettingsWidget import SinkInputSettingsWidget

class InputSinkUI(SinkUI):

    def __init__(self , parent):
        self.mouse_pressed = False
        SinkUI.__init__(self, parent)
        self.setContentsMargins(0,0,0,0)

    def init(self):
        SinkUI.init(self)
        self.setAcceptDrops(False)
        self.layout.setContentsMargins(6,2,6,0)
        
    def createMute(self):
        self.mute = InputMuteButton(self)
        self.mute.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed,True) )
        self.connect(self.mute, SIGNAL("clicked()"), self.on_mute_cb )

    def create_settings_widget(self):
        self.settings_widget = SinkInputSettingsWidget(self.veromix, self)
        self.settings_widget.update_with_info(self.pa_sink)

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
        if self.veromix.get_meter_visible():
            self.panel_layout.addItem(self.meter)
            self.meter.show()
        else:
            self.meter.hide()

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


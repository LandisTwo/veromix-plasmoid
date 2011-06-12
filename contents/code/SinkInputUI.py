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
        self.setAcceptDrops(False)
        self.setContentsMargins(0,0,0,0)
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

    def update_label(self):
        text =  self.pa_sink.name
        bold = self.pa_sink.props["app"]

        iconname = None
        if self.pa_sink.props["app_icon"] != "None":
            iconname = self.pa_sink.props["app_icon"]
        if iconname == None and  self.pa_sink.props["app"] != "None":
            iconname = self.veromix.query_application(self.pa_sink.props["app"])
        if bold == "knotify":
            bold = i18n("System Notifications")
            text = ""
            iconname = 'dialog-information'
        if bold == "npviewer.bin" or bold == "plugin-container":
            bold = i18n("Flash Player")
            text = ""
            iconname = 'flash'
        if bold == "chromium-browser":
            bold = i18n("Chromium Browser")
            text = ""
        if iconname == None:
            iconname = "mixer-pcm"

        if iconname :
            self.mute.setBigIconName(iconname)
            self.updateIcon()

        if self.slider:
            self.slider.setText(text)
            self.slider.setBoldText(bold)
            self.text = bold

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


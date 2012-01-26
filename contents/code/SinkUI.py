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
from Utils import i18n

from Channel import Channel
from SettingsWidget import SinkSettingsWidget

class SinkUI(Channel):
    muteInfo = pyqtSignal(bool)

    def __init__(self , parent):
        self.automatically_muted = False
        self.extended_panel = None
        Channel.__init__(self, parent)
        self.setContentsMargins(0,0,0,0)

    def context_menu_create_custom(self):
        action_device = QAction(i18n("Default Sink"), self.popup_menu)
        self.popup_menu.addAction(action_device)
        action_device.setCheckable(True)
        if self.isDefaultSink():
            action_device.setChecked(True)
            action_device.setEnabled(False)
        else:
            action_device.triggered.connect(self.on_set_default_sink_triggered)
        self.context_menu_create_sounddevices()

    def on_set_default_sink_triggered(self, action):
        if boolean:
            self.pa.set_default_sink(self.index )

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

    def update_label(self):
        text = ""
        try:
            text = self.pa_sink.props["device_name"]
        except:
            pass
        if self.slider:
            self.slider.setBoldText(text)
            self.set_name(text)

## Drag and Drop Support

    def dropEvent(self, dropEvent):
        uris = dropEvent.mimeData().urls()
        for uri in uris:
            if uri.scheme() == "veromix":
                self.pa.move_sink_input(uri.port(), self.index)

    def startDrag(self,event):
        pass

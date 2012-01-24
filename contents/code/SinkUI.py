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


    def contextMenuEvent(self,event):
        self.popup_menu = QMenu()
        profiles_menu = QAction(i18n("Sound Card Profiles"), self.popup_menu)
        self.popup_menu.addAction(profiles_menu)
        self.popup_menu.triggered.connect(self.on_contextmenu_clicked)
        info = self.veromix.card_infos.values()

        self.card_settings = {}
        for card in self.veromix.card_infos.values():
            card_menu = QMenu(card.properties["device.description"], self.popup_menu)
            self.popup_menu.addMenu(card_menu)
            active_profile_name = card.get_active_profile_name()
            self.profiles = card.get_profiles()
            for profile in self.profiles:
                action = QAction(str(profile.description), card_menu)
                self.card_settings[action] = card
                if profile.name == active_profile_name:
                    action.setCheckable(True)
                    action.setChecked(True)
                card_menu.addAction(action)

        self.popup_menu.exec_(event.screenPos())

    def on_contextmenu_clicked(self, action):
        card = self.card_settings[action]
        for profile in card.get_profiles():
            if action.text() == profile.description:
                self.veromix.pa.set_card_profile(card.index, profile.name)

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

    def create_settings_widget(self):
        self.settings_widget = SinkSettingsWidget(self.veromix, self)
        self.settings_widget.update_with_info(self.pa_sink)

## Drag and Drop Support

    def dropEvent(self, dropEvent):
        uris = dropEvent.mimeData().urls()
        for uri in uris:
            if uri.scheme() == "veromix":
                self.pa.move_sink_input(uri.port(), self.index)

    def startDrag(self,event):
        pass

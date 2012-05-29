# -*- coding: utf-8 -*-
# Copyright (C) 2012 Nik Lutz <nik.lutz@gmail.com>
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
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import gettext, dbus
from gi.repository import Gtk
from gi.repository import GObject

from veromixcommon.LADSPAEffects import LADSPAPresetLoader
from veromixcommon.LADSPAEffects import LADSPAEffects

i18n = gettext.gettext

_instance = None
class ContextMenu:
    def get_instance(pa_proxy=None):
        global _instance
        if _instance == None:
            _instance = ContextMenuFactory(pa_proxy)
        return _instance

class ContextMenuFactory(GObject.GObject):

    def __init__(self, veromix):
        GObject.GObject.__init__(self)
        self.card_infos = {}
        self.card_settings = {}
        self.port_actions = {}
        self.menus = []
        self.profiles = []
        self.veromix = veromix
        self._pa_proxy = veromix.pa_proxy()
        self._pa_proxy.connect("on_card_info", self.on_card_info)
        self._pa_proxy.connect("on_card_remove", self.on_remove_card)

    def populate_menu(self, pa_sink_proxy, menu, slider):
        if pa_sink_proxy.is_sinkinput():
            self.create_menu_sinks(pa_sink_proxy, menu)
        if slider.is_ladspa():
            self.context_menu_create_presets(slider, menu)
            self.context_menu_create_effects(slider, menu)
        if pa_sink_proxy.is_sink():
            self.context_menu_create_ports(pa_sink_proxy, menu)
            self.context_menu_create_sounddevices(pa_sink_proxy, menu)
            self.context_menu_create_defaultsink(pa_sink_proxy, menu)
        self.context_menu_create_mute(pa_sink_proxy, menu)
        if not slider.is_ladspa():
            self.context_menu_create_expand(slider, menu)
        if pa_sink_proxy.is_sinkinput() or slider.is_ladspa():
            self.context_menu_create_kill(pa_sink_proxy, menu)
        if pa_sink_proxy.is_sink() and not slider.is_ladspa():
            self.context_menu_create_presets_and_effects(slider, menu)
            self.context_menu_create_sounddevices_other(menu)

# ---- helper methods

    def on_card_info(self, widget, info):
        self.card_infos[info.name] = info

    def on_remove_card(self, widget, index):
        for key in self.card_infos.keys():
            card = self.card_infos[key]
            if int(card.index) == int(index):
                del self.card_infos[key]

    def on_defaultsink_clicked(self, widget, sink):
        sink.be_default_sink()

    def on_mute_clicked(self, widget, sink):
        sink.toggle_mute()

    def on_kill_clicked(self, widget, sink):
        sink.kill()

    def on_expand_clicked(self, widget, slider_widget):
        slider_widget.expand(widget.get_active())

    def on_card_profile_clicked(self, widget, sink):
        if widget in self.card_settings.keys():
            card = self.card_settings[widget]
            for profile in card.get_profiles():
                if widget.get_label() == profile.description:
                    self._pa_proxy.set_card_profile(card.index, profile.name)

    def on_moveto_sink_clicked(self, widget, sinkinput):
        self.sink_actions[widget].move_sink_input(sinkinput.get_index())

    def on_card_port_clicked(self, widget, sink):
        sink.set_port(self.port_actions[widget])

    def context_menu_create_defaultsink(self, sink, popup_menu):
        item = Gtk.CheckMenuItem()
        item.set_active(sink.is_default())
        item.set_label(i18n("Default device"))
        item.connect("activate", self.on_defaultsink_clicked, sink)
        popup_menu.append(item)

    def context_menu_create_kill(self, sink, popup_menu):
        item = Gtk.MenuItem()
        item.set_label(i18n("Kill"))
        item.connect("activate", self.on_kill_clicked, sink)
        popup_menu.append(item)

    def context_menu_create_mute(self, sink, popup_menu):
        item = Gtk.CheckMenuItem()
        item.set_active(sink.isMuted())
        #item.set_draw_as_radio(True)
        item.set_label(i18n("Mute"))
        item.connect("activate", self.on_mute_clicked, sink)
        popup_menu.append(item)

    def context_menu_create_expand(self, slider_widget, popup_menu):
        item = Gtk.CheckMenuItem()
        #item.set_draw_as_radio(True)
        item.set_label(i18n("Unlock Channels"))
        item.set_active(slider_widget.is_expanded())
        item.connect("activate", self.on_expand_clicked, slider_widget)
        popup_menu.append(item)

    def create_menu_sinks(self, proxy, popup_menu):
        moveto_menu = Gtk.Menu()
        moveto_menu_item = Gtk.MenuItem(i18n("Move To"))
        moveto_menu_item.set_submenu(moveto_menu)
        self.sink_actions = {}
        sinks = self.veromix.get_sink_widgets()
        for sink in sinks:
            action = Gtk.CheckMenuItem()
            action.set_draw_as_radio(True)
            action.set_label(sink.pa_sink_proxy().get_nice_title())
            self.sink_actions[action] = sink.pa_sink_proxy()
            if proxy.get_output_index() == sink.pa_sink_proxy().get_index():
                action.set_active(True)
            moveto_menu.append(action)
            action.connect("activate", self.on_moveto_sink_clicked, proxy)
        popup_menu.append(moveto_menu_item)

    def context_menu_create_ports(self, sink, popup_menu):
        self.port_actions = {}
        if len(sink.ports.keys()) > 1:
            ports_menu = Gtk.Menu()
            ports_menu_item = Gtk.MenuItem(i18n("Ports"))
            ports_menu_item.set_submenu(ports_menu)
            ports = sink.ports
            for port in ports.keys():
                action = Gtk.CheckMenuItem()
                action.set_draw_as_radio(True)
                action.set_label(ports[port])
                self.port_actions[action]=port
                if port == sink.active_port:
                    action.set_active(True)
                ports_menu.append(action)
                action.connect("activate", self.on_card_port_clicked, sink)
            popup_menu.append(ports_menu_item)

    def context_menu_create_sounddevices(self, sink, popup_menu):
        self.card_settings = {}
        self.menus = []
        for card in self.card_infos.values():
            current = self.get_card_info_for(sink)
            card_menu = None
            if current != None and  current.get_description() == card.get_description():
                card_menu = Gtk.Menu()
                card_menu_item = Gtk.MenuItem()
                card_menu_item.set_label(i18n("Profile"))
                card_menu_item.set_submenu(card_menu)
                popup_menu.append(card_menu_item)
            else:
                card_menu = Gtk.Menu()
                card_menu_item = Gtk.MenuItem()
                card_menu_item.set_label(card.get_description())
                card_menu_item.set_submenu(card_menu)
                self.menus.append(card_menu_item)
            active_profile_name = card.get_active_profile_name()
            self.profiles = card.get_profiles()
            for profile in self.profiles:
                action = Gtk.CheckMenuItem()
                action.set_draw_as_radio(True)
                action.set_label(profile.description)
                self.card_settings[action] = card
                if profile.name == active_profile_name:
                    action.set_active(True)
                action.connect("activate", self.on_card_profile_clicked, sink)
                card_menu.append(action)

    def context_menu_create_sounddevices_other(self, popup_menu):
        if len(self.menus) > 0:
            s = Gtk.SeparatorMenuItem()
            popup_menu.append(s)
            for each in self.menus:
                popup_menu.append(each)

    def get_card_info_for(self, sink):
        card_identifier = dbus.String('alsa.long_card_name') #u'sysfs.path'
        info = self._get_card_info_for(sink, card_identifier)
        if info:
            return info
        card_identifier = dbus.String('device.string')
        info = self._get_card_info_for(sink, card_identifier)
        if info:
            return info
        card_identifier = dbus.String('sysfs.path')
        return self._get_card_info_for(sink, card_identifier)

    def _get_card_info_for(self, sink, card_identifier):
        if sink == None:
            return None
        if card_identifier  not in sink.props.keys():
            return None
        for info in self.card_infos.values():
            if card_identifier  in info.properties.keys():
                if info.properties[dbus.String(card_identifier)] == sink.props[card_identifier]:
                    return info
        return None

    def context_menu_create_presets_and_effects(self, sink, popup_menu):
        effects_menu = Gtk.Menu()
        effects_menu_item = Gtk.MenuItem()
        effects_menu_item.set_label(i18n("Add Effect"))
        effects_menu_item.set_submenu(effects_menu)
        popup_menu.append(effects_menu_item)
        self.context_menu_create_presets(sink, effects_menu)
        self.context_menu_create_effects(sink, effects_menu)

    def context_menu_create_presets(self, slider, popup_menu):
        presets_menu = Gtk.Menu()
        presets_menu_item = Gtk.MenuItem()
        presets_menu_item.set_label(i18n("Preset"))
        presets_menu_item.set_submenu(presets_menu)
        popup_menu.append(presets_menu_item)

        #self.action_save_preset = QAction(i18n("Save"),effect_menu)
            #effect_menu.addAction(self.action_save_preset)
            #if not self.is_preset():
                #self.action_save_preset.setEnabled(False)

            #self.action_save_as_preset = QAction(i18n("Save As..."),effect_menu)
            #effect_menu.addAction(self.action_save_as_preset)
            #effect_menu.addSeparator()
        self.presets_slider = slider
        for preset in LADSPAPresetLoader().presets():
            action = Gtk.CheckMenuItem()
            action.set_draw_as_radio(True)
            action.set_label(preset["preset_name"])
            presets_menu.append(action)
            if slider.get_selected_preset() == preset["preset_name"]:
                action.set_active(True)
            action.connect("activate", self.on_preset_clicked, preset)

    def context_menu_create_effects(self, slider, popup_menu):
        effects_menu = Gtk.Menu()
        effects_menu_item = Gtk.MenuItem()
        effects_menu_item.set_label(i18n("Effect"))
        effects_menu_item.set_submenu(effects_menu)
        popup_menu.append(effects_menu_item)

        self.effect_slider = slider
        for preset in LADSPAEffects().effects():
            action = Gtk.CheckMenuItem()
            action.set_draw_as_radio(True)
            action.set_label(preset["preset_name"])
            effects_menu.append(action)
            if slider.get_selected_effect() == preset["label"]:
                action.set_active(True)
            action.connect("activate", self.on_effect_clicked, preset)

    def on_preset_clicked(self, widget, preset):
        self.presets_slider.set_ladspa_effect(preset["preset_name"], self.presets_slider.get_ladspa_master())

    def on_effect_clicked(self, widget, preset):
        self.effect_slider.set_ladspa_effect(preset["preset_name"], self.effect_slider.get_ladspa_master())


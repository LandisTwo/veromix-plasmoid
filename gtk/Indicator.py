#!/usr/bin/python3
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

from gi.repository import Gtk, Gdk

class Indicator:
    def __init__(self, iconname, veromix):
        self.window = veromix.window
        self.veromix = veromix
        self.menu = Gtk.Menu()
        self.indicator = None

        self.APPIND_SUPPORT = True
        try: from gi.repository import AppIndicator3
        except: self.APPIND_SUPPORT = False

        if self.APPIND_SUPPORT:
            self.indicator = AppIndicator3.Indicator.new("Veromix", iconname, AppIndicator3.IndicatorCategory.APPLICATION_STATUS)
            self.indicator.set_status (AppIndicator3.IndicatorStatus.ACTIVE)
            self.indicator.set_menu(self.menu)
            self.indicator.connect("scroll-event", self.on_scroll_wheel)
#            self.indicator.connect("menu-show", self.toggle_window)

            toggle = Gtk.MenuItem()
            toggle.set_label("Toggle Window")
            toggle.connect("activate", self.toggle_window)

            mute = Gtk.MenuItem()
            mute.set_label("Mute")
            mute.connect("activate", self.on_middle_click)
            self.menu.append(mute)
            self.indicator.set_secondary_activate_target(mute)
            self.menu.append(toggle)
        else:
            self.status_icon = Gtk.StatusIcon()
            self.status_icon.set_from_icon_name(iconname)
            self.status_icon.connect('popup-menu', self.on_right_click_statusicon)
            self.status_icon.connect("activate", self.toggle_window)
            self.status_icon.connect('scroll_event', self.on_scroll_wheel)
            self.status_icon.connect("button_press_event", self.on_status_icon_clicked)

        quit = Gtk.MenuItem()
        quit.set_label("Quit")
        quit.connect("activate", Gtk.main_quit)
        self.menu.append(quit)

        self.menu.show_all()

    def on_status_icon_clicked(self, widget, event):
        if event.button == 2:
#        if event.type == Gdk.EventType._2BUTTON_PRESS:
            self.on_middle_click(event)
            return True
        return False

    def on_middle_click(self, event):
        self.veromix.get_default_sink().toggle_mute()

    def on_scroll_wheel(self, widget, event, value = None):
        if self.APPIND_SUPPORT:
            self.veromix.get_default_sink().step_volume((value == 0))
        else:
            if event.direction  == Gdk.ScrollDirection.DOWN or event.direction  == Gdk.ScrollDirection.LEFT:
                self.veromix.get_default_sink().step_volume(False)
            if event.direction  == Gdk.ScrollDirection.UP or event.direction  == Gdk.ScrollDirection.RIGHT:
                self.veromix.get_default_sink().step_volume(True)

    def toggle_window(self, widget):
        if not self.window.is_active():
            self.window.present()
        else:
            self.window.hide()

    def get_tray_menu(self):
        return self.menu

    def on_right_click_statusicon(self, icon, button, time):
        self.get_tray_menu()
        def pos(menu, aicon):
            return (Gtk.StatusIcon.position_menu(menu, aicon))
        self.menu.popup(None, None, pos, icon, button, time)

    def on_sink_info(self, index, info, sink_box):
        channel = sink_box.get_default_sink()
        if channel == None:
            return
        volume = channel.pa_sink_proxy().get_volume()
        if channel.pa_sink_proxy().is_muted():
            self.set_icon("audio-volume-muted")
        elif volume > 75:
            self.set_icon("audio-volume-high")
        elif volume > 30:
            self.set_icon("audio-volume-medium")
        elif volume > -5:
            self.set_icon("audio-volume-low")

    def set_icon(self, iconname):
        if self.APPIND_SUPPORT:
            self.indicator.set_icon(iconname)
        else:
            self.status_icon.set_from_icon_name(iconname)


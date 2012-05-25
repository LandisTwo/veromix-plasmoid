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

##
# python3-gi python3-dbus
##
import os, gettext, dbus
from gi.repository import Gtk, Gdk

from Veromix import Veromix
from Indicator import Indicator
from Configuration import config
from veromixcommon.Utils import createDbusServiceDescription

VEROMIX_BASEDIR = os.path.abspath(os.path.join(os.path.realpath(__file__), os.path.pardir))
VEROMIX_BASEDIR = os.path.abspath(os.path.join(VEROMIX_BASEDIR, os.path.pardir))
VEROMIX_SERVICE = "/dbus-service/veromix-service-glib.py"

class VeromixWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="Veromix",type =Gtk.WindowType.TOPLEVEL)
#        self.set_wmclass ("veromix", "veromix-plasmoid")
#        self.icon = self.render_icon(Gtk.STOCK_FIND, Gtk.IconSize.BUTTON)
        self.icon = self.render_icon("veromix-plasmoid", Gtk.IconSize.BUTTON)
        self.set_icon(self.icon)
#        self.set_type_hint(Gtk.WindowType.TOPLEVEL)
#        Gdk.set_program_class("veromix-plasmoid")
        self.connect('delete-event', self.on_delete_event)

        veromix = Veromix(self)
        self.add(veromix)
        self.create_indicator(veromix)
        self.set_default_size(430, 180)

    def on_delete_event(self, widget, event):
        if config().get_window_exit_on_close():
            Gtk.main_quit()
        self.hide()
        return True

    def create_indicator(self, veromix):
        self.tray_icon = Indicator(veromix)

Gdk.set_program_class("veromix")
win = VeromixWindow()
#win.connect("delete-event", Gtk.main_quit)
win.show_all()

if __name__ == '__main__':
    # Veromix is dedicated to my girlfriend Véronique
    createDbusServiceDescription(VEROMIX_BASEDIR + VEROMIX_SERVICE, False)
    Gtk.main()
    config().save()

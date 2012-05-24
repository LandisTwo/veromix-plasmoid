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

from GPulseAudioProxy import *
from CardProfiles import *
from Indicator import Indicator
from SortedChannelBox import SortedChannelBox

class Veromix(Gtk.VBox):

    def __init__(self, window):
        Gtk.VBox.__init__(self, window)
        self.window = window
        self.pa = PulseAudio(self)

        self.create_sinks()
        self.create_indicator()
        self.launch_pa()

    def launch_pa(self):

        self.pa.connect_veromix_service()
        CardProfiles.get_instance(self)

        self.pa.connect("on_sink_info", self.sink_box.on_sink_info)
        self.pa.connect("on_sink_info", self.tray_icon.on_sink_info, self.sink_box)
        self.pa.connect("on_sink_remove", self.sink_box.on_sink_remove)

        self.pa.connect("on_sink_input_info", self.sink_box.on_sink_input_info)
        self.pa.connect("on_sink_input_remove", self.sink_box.on_sink_remove)

        self.pa.connect("on_source_info", self.source_box.on_source_info)
        self.pa.connect("on_source_remove", self.source_box.on_sink_remove)

        self.pa.connect("on_source_output_info", self.source_box.on_source_output_info)
        self.pa.connect("on_source_output_remove", self.source_box.on_sink_remove)

        self.pa.requestInfo()

    def create_sinks(self):
        self.veromix_sinks = Gtk.VBox()

        self.source_box = SortedChannelBox()
        self.veromix_sinks.pack_start(self.source_box, False, True, 0)

        self.sink_box = SortedChannelBox()
        self.veromix_sinks.pack_start(self.sink_box, False, True, 0)

        spacer = Gtk.HBox()
        self.veromix_sinks.pack_start(spacer,True,True,0)

        self.scroll = Gtk.ScrolledWindow(hadjustment=None, vadjustment=None)
        self.scroll.set_policy(1, 1)
        self.scroll.add_with_viewport(self.veromix_sinks)
        self.scroll.set_border_width(5)

#        self.expander = Gtk.Expander(label="Outputs")
#        self.expander.set_expanded(True)
#        self.expander.add(self.scroll)
#        self.pack_start(self.expander, True, True, 0)

        self.pack_start(self.scroll, True, True, 0)

    def create_indicator(self):
        self.tray_icon = Indicator("audio-volume-medium", self)

    def get_default_sink(self):
        return self.sink_box.get_default_sink()

    def get_sink_widgets(self):
        return self.sink_box.get_sinks()

    def pa_proxy(self):
        return self.pa


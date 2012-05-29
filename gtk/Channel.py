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

import re
from gi.repository import Gtk, Gdk

from SliderWidget import SliderWidget
from LadspaWidget import LadspaWidget
from ContextMenu import ContextMenu

DRAG_ACTION = Gdk.DragAction.COPY
(TARGET_ENTRY_TEXT, TARGET_ENTRY_PIXBUF) = range(2)

class Channel(Gtk.Alignment):

    ICON_HEIGHT = 36

    def __init__(self):
        Gtk.Alignment.__init__(self)
        #self.set_homogeneous(False)
        self._create()
        self._init()
        self.set_size_request(self.ICON_HEIGHT, self.ICON_HEIGHT)
        self._current_icon = None

    def _init(self):
        self.frame = Gtk.Frame()
        self.hbox = Gtk.HBox()
        self.mute.set_size_request(self.ICON_HEIGHT,self.ICON_HEIGHT)

        #self.middle.pack_start(self.label, True, True, 0)
        #self.middle.pack_start(self.slider, True, True, 0)
        #self.hbox.pack_start(self.middle,True,True,5)

        self.mute_box.pack_start(self.mute, False, True, 2)
        self.mute_box.pack_start(Gtk.HBox(), True, True, 0)

        self.hbox.pack_start(self.mute_box, False, True, 2)
        self.hbox.pack_start(self.slider,True,True,5)

        self.frame.add(self.hbox)
        self.add(self.frame)
        self.connect("button-press-event", self.on_button_press_event)

    def _create(self):
        self._create_mute()
        self._create_slider()
        #self._create_middle()

    def _create_mute(self):
        self.mute_box = Gtk.VBox()
        self.mute = Gtk.ToggleButton()
        self.mute.set_image_position(1)
        self.mute.connect("released", self.on_muted_clicked)

    #def _create_mute(self):
        ##self.mute = Gtk.ToggleButton()
        #self.mute = Gtk.Image()
        ##self.mute.set_image_position(1)
        ##self.mute.connect("clicked", self.on_muted_clicked)

    #def _create_middle(self):
        #self.middle = Gtk.VBox()
        #self.middle.set_border_width(0)
        ##self.middle.set_homogeneous(True)

    def _create_slider(self):
        self.slider = SliderWidget()

    def on_button_press_event(self, widget, event):
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 3:
            self.menu = Gtk.Menu()
            instance = ContextMenu.get_instance()
            instance.populate_menu(self.pa_sink_proxy(), self.menu, self.slider)
            self.menu.show_all()
            self.menu.popup(None, None, None, None, event.button, event.time)
            return True # event has been handled

    def on_muted_clicked(self, button):
        self.pa_sink_proxy().toggle_mute()

    def pa_sink_proxy(self):
        return self._pa_sink

    def on_pa_data_updated(self, data):
        self._pa_sink = data

        self.slider.set_volume(data)
        self.mute.set_active(data.isMuted())

        if self._current_icon != data.get_nice_icon():
            image = Gtk.Image()
            image.set_from_icon_name(data.get_nice_icon(), Gtk.IconSize.BUTTON)
            self.mute.set_image(image)
            self._current_icon = data.get_nice_icon()

    def step_volume(self, up):
        self.slider.step_volume(up)

    def toggle_mute(self):
        self.pa_sink_proxy().toggle_mute()

    def on_pa_module_data_updated(self, data):
        pass

class SinkChannel(Channel):

    def _init(self):
        Channel._init(self)
        self.drag_dest_set(Gtk.DestDefaults.ALL, [], DRAG_ACTION)
        #self.drag_dest_add_uri_targets()
        #self.drag_dest_add_text_targets()
        #self.drag_dest_add_uri_targets()
        self.drag_dest_add_text_targets()
        self.connect("drag-data-received", self.on_drag_data_received)

    def on_drag_data_received(self, widget, drag_context, x, y, data, info, time):
        if info == TARGET_ENTRY_TEXT:
            match =  re.match("veromix://sink_input_index:(\d*)", data.get_text())
            if match:
                print (match.group(1))
                self.pa_sink_proxy().move_sink_input(match.group(1))
                print ("veromix text: %s" % match.group(1))
            else:
                print ("Received text: %s" % data.get_text())

class SinkInputChannel(Channel):

    def _init(self):
        Channel._init(self)
        #self.set_padding(padding_top, padding_bottom, padding_left, padding_right)
        self.set_padding(0, 0, self.ICON_HEIGHT / 2, 0)

        self.drag_source_set(Gdk.ModifierType.BUTTON1_MASK, [], DRAG_ACTION)
        self.mute.drag_source_set(Gdk.ModifierType.BUTTON1_MASK, [], DRAG_ACTION)
        #self.label.drag_source_set(Gdk.ModifierType.BUTTON1_MASK, [], DRAG_ACTION)
        #self.middle.drag_source_set(Gdk.ModifierType.BUTTON1_MASK, [], DRAG_ACTION)

        self.drag_source_add_text_targets()
        #self.label.drag_source_add_uri_targets()
        self.mute.drag_source_add_text_targets()

        #self.drag_source_add_uri_targets()
        #self.mute.drag_source_add_uri_targets()

        self.connect("drag-data-get", self.on_drag_data_get)
        self.mute.connect("drag-data-get", self.on_drag_data_get)
        #self.label.connect("drag-data-get", self.on_drag_data_get)

    def on_drag_data_get(self, widget, drag_context, data, info, time):
        data.set_text("veromix://sink_input_index:"+str(self.pa_sink_proxy().get_index()), -1)


class SourceChannel(Channel):

    def _init(self):
        Channel._init(self)
        #self.set_padding(padding_top, padding_bottom, padding_left, padding_right)
#        self.set_padding(0, 0, self.ICON_HEIGHT / 2, 0)

class SourceOutputChannel(Channel):

    def _init(self):
        Channel._init(self)
        #self.set_padding(padding_top, padding_bottom, padding_left, padding_right)
        self.set_padding(0, 0, self.ICON_HEIGHT / 2, 0)

class LadspaChannel(SinkChannel):

    def _create_slider(self):
        self.slider = LadspaWidget()

    def on_pa_module_data_updated(self, data):
        self.slider.on_pa_module_data_updated(data, self.pa_sink_proxy())


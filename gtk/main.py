#!/usr/bin/python3

##
# python3-gi python3-dbus
##
import os, gettext, dbus
from gi.repository import Gtk, Gdk
from GPulseAudioProxy import *
from CardProfiles import *

from SortedChannelBox import SortedChannelBox
from veromixcommon.Utils import *

#VEROMIX_BASEDIR = os.path.abspath(os.path.join(os.getcwd(), os.path.pardir))
VEROMIX_BASEDIR = os.path.abspath(os.path.join(os.path.realpath(__file__), os.path.pardir))
VEROMIX_BASEDIR = os.path.abspath(os.path.join(VEROMIX_BASEDIR, os.path.pardir))

VEROMIX_SERVICE = "/dbus-service/veromix-service-glib.py"

class IconoTray:
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

class Veromix(Gtk.VBox):

    def __init__(self, window):
        Gtk.VBox.__init__(self, window)
        self.window = window
        self.pa = PulseAudio(self)
        
        self.create_sinks()
        self.create_indicator()
        self.launch_pa()
        
    def launch_pa(self):
        createDbusServiceDescription(VEROMIX_BASEDIR + VEROMIX_SERVICE)
        
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
        self.tray_icon = IconoTray("audio-volume-medium", self)

    def get_default_sink(self):
        return self.sink_box.get_default_sink()

    def get_sink_widgets(self):
        return self.sink_box.get_sinks()

    def pa_proxy(self):
        return self.pa
    
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
        self.set_default_size(430, 180)        

    def on_delete_event(self, widget, event):
        self.hide()
        return True  

Gdk.set_program_class("veromix-gtk")
win = VeromixWindow()
#win.connect("delete-event", Gtk.main_quit)
win.show_all()

if __name__ == '__main__':
    Gtk.main()

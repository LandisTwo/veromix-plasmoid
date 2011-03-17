# -*- coding: utf-8 -*-
# copyright 2010  Nik Lutz
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

import signal
import dbus.mainloop.qt
from PyQt4.QtCore import *

class SinkChannel(QObject):
    
    def __init__(self, name, volume):
        QObject.__init__(self)
        self.name = name
        self.volume = volume
        
    def getName(self) :
        return self.name
    
    def getVolume(self):
        return self.volume

class SinkInfo(QObject):

    def __init__(self, pulseaudio, index,   name,  muted  , volume ,  props):
        QObject.__init__(self)
        self.pa = pulseaudio
        self.index =  index
        self.name =   name
        self.mute  =   muted
        self. volume  =   volume
        self.props = props
            
    def getVolume(self):
        val =0
        for t in self.volume.keys():
            val += self.volume[t].values()[0]
        return int(val/ len(self.volume.keys()))

    ##def getVolumes(self):
        ##return self.volumes        

    def getChannels(self):
        channels = []
        for key in self.volume.keys():
            t = self.volume[key]
            name = t.keys()[0]
            vol = t.values()[0]
            channels.append(SinkChannel(name,vol))
        return channels

    def volumeDiffFor(self, value):
        vol = []
        diff = self.getVolume() - value
        for key in self.volume.keys():
            value = self.volume[key].values()[0] - diff
            if value < 0:
                value = 0
            vol.append(value )
        return vol
        
class CardProfile:
    def __init__(self, name, properties):
        self.name = name
        self.description = properties["description"]
        # FIXME other values

class CardInfo:
    def __init__(self, index,   name,  properties, active_profile_name ,  profiles_dict):
         self.index = index
         self.name = name
         self.properties = properties
         self.active_profile_name = active_profile_name
         self.profiles_dict = profiles_dict
         self.profiles = []
         for key in self.profiles_dict.keys():
             self.profiles.append(CardProfile(key, self.profiles_dict[key] ))

    def get_profiles(self):
        return self.profiles
        
    def get_active_profile(self):
        for profile in self.card_profiles():
            if self.active_profile_name == profile.name:
                return profile
        return None
        
    def get_active_profile_name(self):
        return self.active_profile_name
        
class PulseAudio(QObject):
    mpris2_properties_changed = pyqtSignal(str,dict)
    
    def __init__(self, parent ):
        QObject.__init__(self)
        REQUIRED_SERVICE_VERSION = 5
        if not dbus.get_default_main_loop():
            mainloop=dbus.mainloop.qt.DBusQtMainLoop(set_as_default=True)
        else:
            mainloop=dbus.mainloop.qt.DBusQtMainLoop(set_as_default=False)
        self.bus = dbus.SessionBus()

        if  self.getMixer().veromix_service_version() != REQUIRED_SERVICE_VERSION:
            try:
                self.getMixer().veromix_service_quit()
                if  self.getMixer().veromix_service_version() != REQUIRED_SERVICE_VERSION:
                    raise NameError("Wrong server versions")
            except:
                raise NameError("Wrong server versions")

        # no exception on startup:
        self.bus.add_signal_receiver(self.on_sink_input_info,
                dbus_interface="org.veromix.notification",
                signal_name="sink_input_info")

        self.bus.add_signal_receiver(self.on_sink_info,
                dbus_interface="org.veromix.notification",
                signal_name="sink_info")

        self.bus.add_signal_receiver(self.on_source_output_info,
                dbus_interface="org.veromix.notification",
                signal_name="source_output_info")

        self.bus.add_signal_receiver(self.on_source_info,
                dbus_interface="org.veromix.notification",
                signal_name="source_info")

        self.bus.add_signal_receiver(self.on_sink_input_remove,
                dbus_interface="org.veromix.notification",
                signal_name="sink_input_remove")

        self.bus.add_signal_receiver(self.on_sink_remove,
                dbus_interface="org.veromix.notification",
                signal_name="sink_remove")

        self.bus.add_signal_receiver(self.on_source_remove,
                dbus_interface="org.veromix.notification",
                signal_name="source_remove")

        self.bus.add_signal_receiver(self.on_source_output_remove,
                dbus_interface="org.veromix.notification",
                signal_name="source_output_remove")

        self.bus.add_signal_receiver(self.on_volume_meter_sink_input,
                dbus_interface="org.veromix.notification",
                signal_name="volume_meter_sink_input")

        self.bus.add_signal_receiver(self.on_volume_meter_source,
                dbus_interface="org.veromix.notification",
                signal_name="volume_meter_source")

        self.bus.add_signal_receiver(self.on_volume_meter_sink,
                dbus_interface="org.veromix.notification",
                signal_name="volume_meter_sink")
                
        self.bus.add_signal_receiver(self.on_card_info,
                dbus_interface="org.veromix.notification",
                signal_name="card_info")
        #pa_obj  = bus.get_object("org.veromix.pulseaudioservice","/org/veromix/pulseaudio")
        #interface = dbus.Interface(pa_obj,dbus_interface="org.veromix.notification")
        #interface.connect_to_signal("sink_input_info", self.on_sink_input_info)
        #interface.connect_to_signal("sink_info", self.on_sink_info)
        #interface.connect_to_signal("sink_input_remove", self.on_sink_input_remove)
        #interface.connect_to_signal("sink_remove", self.on_sink_remove)

        ##rbplayerobj = bus.get_object("org.veromix.pulseaudio", '/org/veromix/pulseaudio')
        #pa_obj  = bus.get_object("org.veromix.pulseaudioservice","/org/veromix/pulseaudio")
        #self.mixer = dbus.Interface(pa_obj, 'org.veromix.pulseaudio')

    def connect_mpris2_player(self, callback, name):
        self.bus.add_signal_receiver(callback ,
                dbus_interface="org.freedesktop.DBus.Properties",
                signal_name="PropertiesChanged",
                bus_name=name)

    def on_mpris2_properties_changed(self, interface, properties, signature):
        self.mpris2_properties_changed.emit(str(interface), properties)

    def getMixer(self):
        pa_obj  = self.bus.get_object("org.veromix.pulseaudioservice","/org/veromix/pulseaudio")
        return dbus.Interface(pa_obj, 'org.veromix.pulseaudio')

    def getNowPlayingObj(self, destination):
        return  self.bus.get_object(destination, '/org/mpris/MediaPlayer2')

    def getNowPlaying(self, destination):
        pa_obj = self.getNowPlayingObj(destination)
        #pa_obj  = self.bus.get_object("org.mpris.amarok","/Player")
        return dbus.Interface(pa_obj, 'org.mpris.MediaPlayer2.Player')
        
    def getNowPlayingProperty(self, destination, name):
        pa_obj = self.getNowPlayingObj(destination)
        props = dbus.Interface(pa_obj, 'org.freedesktop.DBus.Properties')
        return props.Get('org.mpris.MediaPlayer2.Player', name )
        #rbprops.Set('org.gnome.Rhythmbox.Shell', 'visibility', force_visible or (not is_visible))

    def on_sink_input_info(self,   index,   name,  muted  , volume ,  props):
        sink =SinkInfo(self, index,   name,  muted  , volume ,  props)
        self.emit(SIGNAL("on_sink_input_info(PyQt_PyObject)"), sink )

    def on_sink_info(self,  index,   name,  muted  , volume ,  props):
        sink = SinkInfo( self,  index,   name,  muted  , volume,  props)
        self.emit(SIGNAL("on_sink_info(PyQt_PyObject)"), sink )

    def on_source_output_info(self,  index,   name, props):
        sink = SinkInfo( self,  index,   name, True, {"left":0, "right":0},  props)
        self.emit(SIGNAL("on_source_output_info(PyQt_PyObject)"), sink )

    def on_source_info(self,  index,   name,  muted  , volume ,  props):
        sink = SinkInfo( self,  index,   name,  muted  , volume , props)
        self.emit(SIGNAL("on_source_info(PyQt_PyObject)"), sink )

    def on_sink_input_remove(self, index):
        self.emit(SIGNAL("on_sink_input_remove(int)"), index )

    def on_sink_remove(self, index):
        self.emit(SIGNAL("on_sink_remove(int)"), index )

    def on_source_remove(self, index):
        self.emit(SIGNAL("on_source_remove(int)"), index )

    def on_source_output_remove(self, index):
        self.emit(SIGNAL("on_source_output_remove(int)"), index )

    def on_volume_meter_sink_input(self, index, value):
        self.emit(SIGNAL("on_volume_meter_sink_input(int,float)"), index ,value)
        
    def on_volume_meter_sink(self, index, value):
        self.emit(SIGNAL("on_volume_meter_sink(int,float)"), index ,value)

    def on_volume_meter_source(self, index, value):
        self.emit(SIGNAL("on_volume_meter_source(int,float)"), index ,value)

    def on_card_info(self, index, name, properties, active_profile_name, profiles_dict):
        info = CardInfo( index, name, properties, active_profile_name, profiles_dict)
        self.emit(SIGNAL("on_card_info(PyQt_PyObject)"), info)
        
    # calls

    def set_sink_input_volume(self, index, vol):
        try:
            self.getMixer().sink_input_volume(index,vol)
        except Exception, e:
            print "dbus connection not ready: "

    def set_sink_input_mute(self, index, mute):
        self.getMixer().sink_input_mute(index,mute)

    def sink_input_kill(self, index):
        self.getMixer().sink_input_kill(index)

    def set_sink_volume(self, index, vol):
        self.getMixer().sink_volume(index,vol)

    def set_sink_mute(self, index, mute):
        self.getMixer().sink_mute(index,mute)

    def set_default_sink(self, index):
        self.getMixer().set_default_sink(index)

    def set_source_volume(self, index, vol):
        self.getMixer().source_volume(index,vol)

    def set_source_mute(self, index, mute):
        self.getMixer().source_mute(index,mute)

    def set_default_source(self, index):
        self.getMixer().set_default_source(index)

    def move_sink_input(self, sink, output):
        self.getMixer().move_sink_input(sink, output)

    def move_source_output(self, sink, output):
        self.getMixer().move_source_output(sink, output)

    def toggle_monitor_of_sink(self, sink_index, named):
        self.getMixer().toggle_monitor_of_sink(sink_index, named)

    def toggle_monitor_of_sinkinput(self, sinkinput_index, sink_index, named):
        self.getMixer().toggle_monitor_of_sinkinput(sinkinput_index, sink_index, named)

    def toggle_monitor_of_source(self,  source_index, named):
        self.getMixer().toggle_monitor_of_source( source_index, named)

    # FIXME

    def nowplaying_next(self, destination):
        self.getNowPlaying(str(destination)).Next()

    def nowplaying_prev(self, destination):
        self.getNowPlaying(str(destination)).Previous()
        
    def nowplaying_pause(self, destination):
        self.getNowPlaying(str(destination)).Pause()        
    
    def nowplaying_play(self, destination):
        self.getNowPlaying(str(destination)).Play()        

    def nowplaying_getPosition(self, destination):
        return self.getNowPlayingProperty( str(destination) , "Position" )

    def nowplaying_getMetadata(self, destination):
        return self.getNowPlayingProperty( str(destination) , "Metadata" )

    def nowplaying_getPlaybackStatus(self, destination):
        return self.getNowPlayingProperty( str(destination) , "PlaybackStatus" )
        
    def requestInfo(self):
        try:
            self.getMixer().requestInfo()
        except Exception, e:
            print "dbus connection not ready: " , e

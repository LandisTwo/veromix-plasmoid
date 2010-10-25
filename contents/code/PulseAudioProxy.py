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
#from PyQt4.QtDBus import *


class SinkInfo(QObject):
    
    def __init__(self, pulseaudio, index,   name,  muted  , volume ,  props):    
        QObject.__init__(self)
        self.pa = pulseaudio
        self.index =  index 
        self.name =   name
        self.mute  =   muted
        self. volume  =   volume
        #self.client_index = client_index  
        #self.client_name = client_name
        self.props = props

    def getVolume(self):
        return self.volume["left"]     
    
        
class PulseAudio(QObject):

    def __init__(self, parent ):
        QObject.__init__(self)
        REQUIRED_SERVICE_VERSION = 1
        if not dbus.get_default_main_loop():
            mainloop=dbus.mainloop.qt.DBusQtMainLoop(set_as_default=True)
        else:
            mainloop=dbus.mainloop.qt.DBusQtMainLoop(set_as_default=False)
        self.bus = dbus.SessionBus()
        
        if  self.getMixer().veromix_service_version() != REQUIRED_SERVICE_VERSION:
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


        #pa_obj  = bus.get_object("org.veromix.pulseaudioservice","/org/veromix/pulseaudio")
        #interface = dbus.Interface(pa_obj,dbus_interface="org.veromix.notification")
        #interface.connect_to_signal("sink_input_info", self.on_sink_input_info)
        #interface.connect_to_signal("sink_info", self.on_sink_info)
        #interface.connect_to_signal("sink_input_remove", self.on_sink_input_remove)
        #interface.connect_to_signal("sink_remove", self.on_sink_remove)
        
        ##rbplayerobj = bus.get_object("org.veromix.pulseaudio", '/org/veromix/pulseaudio')
        #pa_obj  = bus.get_object("org.veromix.pulseaudioservice","/org/veromix/pulseaudio")
        #self.mixer = dbus.Interface(pa_obj, 'org.veromix.pulseaudio') 

    def getMixer(self):
        pa_obj  = self.bus.get_object("org.veromix.pulseaudioservice","/org/veromix/pulseaudio")
        return dbus.Interface(pa_obj, 'org.veromix.pulseaudio') 
        
    def on_sink_input_info(self,   index,   name,  muted  , volume ,  props):
        sink =SinkInfo(self, index,   name,  muted  , volume ,  props)
        self.emit(SIGNAL("on_sink_input_info(PyQt_PyObject)"), sink )
        
    def on_sink_info(self,  index,   name,  muted  , volume ,  props):
        sink = SinkInfo( self,  index,   name,  muted  , volume,  props)
        self.emit(SIGNAL("on_sink_info(PyQt_PyObject)"), sink )        
        
    def on_source_output_info(self,  index,   name, props):
        #print "source_output_info"
        sink = SinkInfo( self,  index,   name, True, {"left":0, "right":0},  props)
        self.emit(SIGNAL("on_source_output_info(PyQt_PyObject)"), sink )
        
    def on_source_info(self,  index,   name,  muted  , volume ,  props):
        #print "on_source_info"
        sink = SinkInfo( self,  index,   name,  muted  , volume , props)
        self.emit(SIGNAL("on_source_info(PyQt_PyObject)"), sink )
    
    def on_sink_input_remove(self, index):
        self.emit(SIGNAL("on_sink_input_remove(int)"), index )

    def on_sink_remove(self, index):
        self.emit(SIGNAL("on_sink_remove(int)"), index )

    def on_source_remove(self, index):
        #print "on_source_remove"
        self.emit(SIGNAL("on_source_remove(int)"), index )
        
    def on_source_output_remove(self, index):
        #print "on_source_output_remove"
        self.emit(SIGNAL("on_source_output_remove(int)"), index )

    def on_volume_meter_sink_input(self, index, value):
        self.emit(SIGNAL("on_volume_meter_sink_input(int,float)"), index ,value)
        
    def on_volume_meter_source(self, index, value):
        self.emit(SIGNAL("on_volume_meter_source(int,float)"), index ,value)
        

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

    def trigger_volume_updates(self):
        self.getMixer().trigger_volume_updates()
        
    def move_sink_input(self, sink, output):
        self.getMixer().move_sink_input(sink, output)
        
    def move_source_output(self, sink, output):
        self.getMixer().move_source_output(sink, output)        
        
    def requestInfo(self):
        try:
            self.getMixer().requestInfo()
        except Exception, e:
            print "dbus connection not ready: " , e

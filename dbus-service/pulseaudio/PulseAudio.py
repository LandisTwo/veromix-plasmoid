# -*- coding: utf-8 -*-
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


## this version is a mix from earcandy and pulsecaster

from lib_pulseaudio import *
import sys
import os
import ctypes
import random
import time

from PulseSink      import PulseSinkInputInfo, PulseSinkInfo
from PulseSource    import PulseSourceOutputInfo, PulseSourceInfo
from PulseClient    import PulseClientCtypes
from PulseCard      import CardInfo

from PyQt4.QtCore import *

PA_VOLUME_CONVERSION_FACTOR = 655.36

# A null method that can be given to pulse methods
def null_cb(a=None, b=None, c=None, d=None):
    #print "NULL CB"
    return

class PulseAudio(QObject):
    def __init__(self):
        QObject.__init__(self)
        self.sinks = {}
        self.sink_inputs = {}
        self.sources = {}
        self.loaded_modules = []
        self.monitor_sinks = {}
        self.monitor_sources = {}
        self.module_stream_restore_argument = ""
        self.default_source_name = ""
        self.default_sink_name = ""


    def start_pulsing(self):
        self.pa_mainloop = pa_threaded_mainloop_new();
        pa_threaded_mainloop_start(self.pa_mainloop)
        pa_threaded_mainloop_lock (self.pa_mainloop)
        self.pa_mainloop_api = pa_threaded_mainloop_get_api(self.pa_mainloop);
        veromix = "VeroMix"
        self._context = pa_context_new(self.pa_mainloop_api, veromix);
        self._context_notify_cb = pa_context_notify_cb_t(self.context_notify_cb)
        pa_context_set_state_callback(self._context, self._context_notify_cb, None)
        pa_context_connect(self._context, None, 0, None)
        ##
        pa_threaded_mainloop_unlock (self.pa_mainloop)

    def pa_exit(self):
        #try:
        ##pa_context_exit_daemon(self._context , self._context_notify_cb , 0 )
        pa_threaded_mainloop_lock (self.pa_mainloop)
        #pa_context_set_state_callback(self._context, None, None)
        #pa_context_disconnect(self._context)
        pa_context_unref(self._context)
        pa_threaded_mainloop_unlock (self.pa_mainloop)

        #pa_threaded_mainloop_stop(self.pa_mainloop)
        pa_threaded_mainloop_free(self.pa_mainloop)
        #pa_threaded_mainloop_wait(self.pa_mainloop)
        self.pa_mainloop_api = None
        self.pa_mainloop = None
        self._context = None
        self.sink_inputs = {}
        self.loaded_modules = []
        self.monitor_sinks = {}
        self._context_notify_cb = None

        self._pa_stream_request_cb = None
        self._null_cb =  None
        self._pa_context_success_cb = None
        self._pa_stream_request_cb  = None
        self._pa_stream_notify_cb  = None
        self._pa_sink_info_cb  = None
        self._pa_card_info_cb = None
        self._pa_context_subscribe_cb  = None
        self._pa_source_info_cb  = None
        self._pa_source_output_info_cb  = None
        self._pa_sink_input_info_list_cb  = None
        self._pa_client_info_list_cb  = None
        self._pa_module_info_cb = None
        self._pa_context_index_cb  = None
        self.module_stream_restore_argument = ""
        #except Exception ,e:
            #print "Except---------------",

#############
    
    def pulse_toggle_monitor_of_sinkinput(self, sinkinput_index, sink_index, name):
        if float(sinkinput_index) in self.monitor_sinks.keys():
            self.pa_disconnect_monitor_of_sinkinput(sinkinput_index)
        else:
            self.pa_create_monitor_stream_for_sink_input(sinkinput_index, sink_index, name)
          
    def pa_disconnect_monitor_of_sinkinput(self, sinkinput_index):
        if float(sinkinput_index) in self.monitor_sinks.keys():
            pa_stream_disconnect(self.monitor_sinks[float(sinkinput_index)])
            del self.monitor_sinks[float(sinkinput_index)]
    
    def pa_create_monitor_stream_for_sink_input(self, index,sink_index,  name, force = False):
        if not index in self.monitor_sinks.keys() or force :
            # Create new stream
            ss = pa_sample_spec()
            ss.channels = 1
            ss.format = 5
            ss.rate = 10
            pa_stream = pa_stream_new(self._context, "Sinkinput Peak detect - ", ss, None)
            pa_stream_set_monitor_stream(pa_stream, index)
            pa_stream_set_read_callback(pa_stream, self._pa_stream_request_cb, index)
            pa_stream_set_suspended_callback(pa_stream, self._pa_stream_notify_cb, None)
            
            pa_stream_connect_record(pa_stream, str(sink_index), None, PA_STREAM_PEAK_DETECT)
            self.monitor_sinks[float(index)] =  pa_stream

###########

    def pulse_toggle_monitor_of_sink(self, sink_index, name):
        if float(sink_index) in self.monitor_sinks.keys():
            self.pa_disconnect_monitor_of_sink(sink_index)
        else:
            self.pa_create_monitor_stream_for_sink(sink_index, name)

    def pa_disconnect_monitor_of_sink(self, sink_index):
        if float(sink_index) in self.monitor_sinks.keys():
            pa_stream_disconnect(self.monitor_sinks[float(sink_index)])
            del self.monitor_sinks[float(sink_index)]

    def pa_create_monitor_stream_for_sink(self, index,  name, force = False):
        if not index in self.monitor_sinks.keys() or force :
            if float(index) not in self.sinks.keys():
                return
            samplespec = pa_sample_spec()
            samplespec.channels = 1
            samplespec.format = 5
            samplespec.rate = 10
            pa_stream = pa_stream_new(self._context, "Sink Peak detect - " + name, samplespec, None)
            pa_stream_set_read_callback(pa_stream, self._pa_sink_stream_request_cb, index+1)
            pa_stream_set_suspended_callback(pa_stream, self._pa_stream_notify_cb, None)

            sink = self.sinks[float(index)]
            pa_stream_connect_record(pa_stream, str(sink.monitor_source) , None, PA_STREAM_PEAK_DETECT)
            self.monitor_sinks[float(index)] =  pa_stream

###########

    def pulse_toggle_monitor_of_source(self, source_index, name):
        if float(source_index) in self.monitor_sources.keys():
            self.pa_disconnect_monitor_of_source(source_index)
        else:
            self.pa_create_monitor_for_source(source_index, self.sources[float(source_index)], name)

    def pa_disconnect_monitor_of_source(self, source_index):
        if float(source_index) in self.monitor_sources.keys():
            pa_stream_disconnect(self.monitor_sources[float(source_index)])
            del self.monitor_sources[float(source_index)]

    def pa_create_monitor_for_source(self, index,source, name, force = False):
        if not index in self.monitor_sources or force :
            # Create new stream
            samplespec = pa_sample_spec()
            samplespec.channels = 1
            samplespec.format = 5
            samplespec.rate = 10

            pa_stream = pa_stream_new(self._context, "Source Peak detect - " + name, samplespec, None)
            pa_stream_set_read_callback(pa_stream, self._pa_source_stream_request_cb, index)
            pa_stream_set_suspended_callback(pa_stream, self._pa_stream_notify_cb, None)

            device = pa_xstrdup( source.name )
            pa_stream_connect_record(pa_stream, device , None, PA_STREAM_PEAK_DETECT)
            self.monitor_sources[float(index)] = pa_stream


############# callbacks
    def pa_context_index_cb(self, context, index, user_data):
        # Do nothing....
        return

    def pa_context_success_cb(self, context, c_int,  user_data):
        return

    # pulseaudio connection status
    def context_notify_cb(self, context, userdata):
        try:
            ctc = pa_context_get_state(context)
            if ctc == PA_CONTEXT_READY:
                print "Pulseaudio connection ready..."
                self._null_cb = pa_context_success_cb_t(null_cb)
                self._pa_context_success_cb = pa_context_success_cb_t(self.pa_context_success_cb)
                self._pa_stream_request_cb = pa_stream_request_cb_t(self.pa_stream_request_cb)
                self._pa_source_stream_request_cb = pa_stream_request_cb_t(self.pa_source_stream_request_cb)
                self._pa_sink_stream_request_cb = pa_stream_request_cb_t(self.pa_sink_stream_request_cb)

                self._pa_stream_notify_cb = pa_stream_notify_cb_t(self.pa_stream_request_cb)
                self._pa_sink_info_cb = pa_sink_info_cb_t(self.pa_sink_info_cb)
                self._pa_context_subscribe_cb = pa_context_subscribe_cb_t(self.pa_context_subscribe_cb)
                self._pa_source_info_cb = pa_source_info_cb_t(self.pa_source_info_cb)
                self._pa_source_output_info_cb = pa_source_output_info_cb_t(self.pa_source_output_info_cb)

                self._pa_card_info_cb = pa_card_info_cb_t(self.pa_card_info_cb)
                self._pa_server_info_cb = pa_server_info_cb_t(self.pa_server_info_cb)

                self._pa_sink_input_info_list_cb = pa_sink_input_info_cb_t(self.pa_sink_input_info_cb)
                self._pa_client_info_list_cb = pa_client_info_cb_t(self.pa_client_info_cb)
                self._pa_module_info_cb = pa_module_info_cb_t(self.pa_module_info_cb)
                self._pa_context_index_cb = pa_context_index_cb_t(self.pa_context_index_cb)

                self.requestInfo()

                pa_context_set_subscribe_callback(self._context, self._pa_context_subscribe_cb, None);
                o = pa_context_subscribe(self._context, (pa_subscription_mask_t)
                                               (PA_SUBSCRIPTION_MASK_SINK|
                                                PA_SUBSCRIPTION_MASK_SOURCE|
                                                PA_SUBSCRIPTION_MASK_SINK_INPUT|
                                                PA_SUBSCRIPTION_MASK_SOURCE_OUTPUT|
                                                PA_SUBSCRIPTION_MASK_CLIENT|
                                                PA_SUBSCRIPTION_MASK_SERVER|
                                                PA_SUBSCRIPTION_MASK_CARD), self._null_cb, None)

                #pa_operation_unref(o)

            if ctc == PA_CONTEXT_FAILED :
                self.__print("Connection failed")
                pa_threaded_mainloop_signal(self.pa_mainloop, 0)

            if ctc == PA_CONTEXT_TERMINATED:
                self.__print("Connection terminated")
                #pa_threaded_mainloop_signal(self.pa_mainloop, 0)
                print "leaving veromix.............."

        except Exception, text:
            self.__print("ERROR context_notify_cb %s" % text)

    def requestInfo(self):
        o = pa_context_get_module_info_list(self._context, self._pa_module_info_cb, True)
        pa_operation_unref(o)

        o = pa_context_get_client_info_list(self._context, self._pa_client_info_list_cb, None)
        pa_operation_unref(o)

        o = pa_context_get_server_info(self._context, self._pa_server_info_cb, None)
        pa_operation_unref(o)

        o = pa_context_get_sink_info_list(self._context, self._pa_sink_info_cb, None)
        pa_operation_unref(o)

        o = pa_context_get_sink_input_info_list(self._context, self._pa_sink_input_info_list_cb, True)
        pa_operation_unref(o)

        o = pa_context_get_source_info_list(self._context, self._pa_source_info_cb, True)
        pa_operation_unref(o)

        o = pa_context_get_source_output_info_list(self._context, self._pa_source_output_info_cb, None)
        pa_operation_unref(o)

        o = pa_context_get_card_info_list(self._context, self._pa_card_info_cb, None)
        pa_operation_unref(o)


    def pa_context_subscribe_cb(self, context, event_type, index, user_data):
        try:
            et = event_type & PA_SUBSCRIPTION_EVENT_FACILITY_MASK
            if et == PA_SUBSCRIPTION_EVENT_SERVER:
                o = pa_context_get_server_info(self._context, self._pa_server_info_cb, None)
                pa_operation_unref(o)
                o = pa_context_get_source_info_list(self._context, self._pa_source_info_cb, None)
                pa_operation_unref(o)
                o = pa_context_get_sink_info_list(self._context, self._pa_sink_info_cb, None)
                pa_operation_unref(o)
                
            if et == PA_SUBSCRIPTION_EVENT_CARD:
                if event_type & PA_SUBSCRIPTION_EVENT_TYPE_MASK == PA_SUBSCRIPTION_EVENT_REMOVE:
                    self.emit(SIGNAL("card_remove(int)"),int(index) )
                else:
                    o = pa_context_get_card_info_list(self._context, self._pa_card_info_cb, None)
                    pa_operation_unref(o)
            
            if et == PA_SUBSCRIPTION_EVENT_CLIENT:
                if event_type & PA_SUBSCRIPTION_EVENT_TYPE_MASK == PA_SUBSCRIPTION_EVENT_REMOVE:
                    self.emit(SIGNAL("client_remove(int)"),int(index) )
                else:
                    o = pa_context_get_client_info(self._context, index, self._pa_client_info_list_cb, None)
                    pa_operation_unref(o)

            if et == PA_SUBSCRIPTION_EVENT_SINK_INPUT:
                if event_type & PA_SUBSCRIPTION_EVENT_TYPE_MASK == PA_SUBSCRIPTION_EVENT_REMOVE:
                    self.emit(SIGNAL("sink_input_remove(int)"),  int(index) )
                    if float(index) in self.monitor_sinks.keys():
                        del self.monitor_sinks[float(index)]
                else:
                    o = pa_context_get_sink_input_info(self._context, int(index), self._pa_sink_input_info_list_cb, True)
                    pa_operation_unref(o)

            if et == PA_SUBSCRIPTION_EVENT_SINK:
                if event_type & PA_SUBSCRIPTION_EVENT_TYPE_MASK == PA_SUBSCRIPTION_EVENT_REMOVE:
                    self.emit(SIGNAL("sink_remove(int)"),int(index) )
                else:
                    ## TODO: check other event-types
                    o = pa_context_get_sink_info_list(self._context, self._pa_sink_info_cb, None)
                    #o = pa_context_get_sink_info_list(self._context, self._pa_source_info_cb, None)
                    pa_operation_unref(o)

            if et == PA_SUBSCRIPTION_EVENT_SOURCE:
                if event_type & PA_SUBSCRIPTION_EVENT_TYPE_MASK == PA_SUBSCRIPTION_EVENT_REMOVE:
                    self.emit(SIGNAL("source_remove(int)"),int(index) )
                    if float(index) in self.monitor_sources.keys():
                        del self.monitor_sources[float(index)]
                else:
                    #o = pa_context_get_source_info_by_index(self._context, int(index), self._pa_source_info_cb, None)
                    o = pa_context_get_source_info_list(self._context, self._pa_source_info_cb, None)
                    pa_operation_unref(o)

            if et == PA_SUBSCRIPTION_EVENT_SOURCE_OUTPUT:
                if event_type & PA_SUBSCRIPTION_EVENT_TYPE_MASK == PA_SUBSCRIPTION_EVENT_REMOVE:
                    self.emit(SIGNAL("source_output_remove(int)"),int(index) )
                else:
                    o = pa_context_get_source_output_info_list(self._context, self._pa_source_output_info_cb, None)
                    #o = pa_context_get_source_info_by_index(self._context,int(index), self._pa_source_output_info_cb, None)
                    pa_operation_unref(o)

        except Exception, text:
            self.__print("pa :: ERROR pa_context_subscribe_cb %s" % text)

    def pa_server_info_cb(self, context, struct, user_data):
        self.default_source_name = struct[0].default_source_name
        self.default_sink_name = struct[0].default_sink_name
        #self.requestInfo()

    def pa_sink_input_info_cb(self, context, struct, index, user_data):
        if struct :
            #if float(struct.contents.sink) in self.sink_inputs:
                #self.pa_create_monitor_stream_for_sink_input(int(struct.contents.index), self.sink_inputs[float(struct.contents.sink)], struct.contents.name)
            sink = PulseSinkInputInfo(struct[0])
            #print ( pa_proplist_to_string(struct.contents.proplist))
            #self.sink_inputs[ float(sink.index) ] = sink
            self.emit(SIGNAL("sink_input_info(PyQt_PyObject)"), sink )

    def pa_sink_info_cb(self, context, struct, index, data):
        if struct:
            sink = PulseSinkInfo(struct[0])
            sink.updateDefaultSink(self.default_sink_name)
            self.sinks[float(sink.index)] = sink
            self.emit(SIGNAL("sink_info(PyQt_PyObject)"), sink )

    def pa_client_info_cb(self, context, struct, c_int, user_data):
        return

    def pa_source_output_info_cb(self, context, struct, cindex, user_data):
        if struct:
            source = PulseSourceOutputInfo(struct[0])
            self.emit(SIGNAL("source_output_info(PyQt_PyObject)"), source )
        return

    def pa_source_info_cb(self, context, struct, eol, user_data):
        if struct:
            source = PulseSourceInfo(struct[0])
            source.updateDefaultSource(self.default_source_name)
            self.sources[ float(struct.contents.index) ] = source
            #if float(struct.contents.index) in self.sources:
                #self.pa_create_monitor_stream_for_source(int(struct.contents.index), source, struct.contents.name)
            self.emit(SIGNAL("source_info(PyQt_PyObject)"), source )

    def pa_card_info_cb(self, context, struct, cindex, user_data):
        if struct:
            info = CardInfo(struct[0])
            self.emit(SIGNAL("card_info(PyQt_PyObject)"), info) 
            #print ( pa_proplist_to_string(struct.contents.proplist))

    def pa_stream_request_cb(self, stream, length, index):
      # This isnt quite right... maybe not a float.. ?
        #null_ptr = ctypes.c_void_p()
        data = POINTER(c_float)()
        pa_stream_peek(stream, data, ctypes.c_ulong(length))
        v = data[length / 4 -1] * 100
        if (v < 0):
            v = 0
        if (v > 100):
            v = 100
        pa_stream_drop(stream)
        if index:
            self.emit(SIGNAL("volume_meter_sink_input(int, float )"),int(index), float(v))

    def pa_source_stream_request_cb(self, stream, length, index):
        # This isnt quite right... maybe not a float.. ?
        #null_ptr = ctypes.c_void_p()
        data = POINTER(c_float)()
        pa_stream_peek(stream, data, ctypes.c_ulong(length))
        v = data[length / 4 -1] * 100
        if (v < 0):
            v = 0
        if (v > 100):
            #print v
            #v = 100
            return
        pa_stream_drop(stream)
        if index:
            self.emit(SIGNAL("volume_meter_source(int, float )"),int(index), float(v))

    def pa_sink_stream_request_cb(self, stream, length, index_incr):
        index = index_incr - 1
        data = POINTER(c_float)()
        pa_stream_peek(stream, data, ctypes.c_ulong(length))
        v = data[length / 4 -1] * 100
        if (v < 0):
            v = 0
        if (v > 100):
            return
        pa_stream_drop(stream)
        self.emit(SIGNAL("volume_meter_sink(int, float )"),int(index), float(v))

    def pa_module_info_cb(self, context, pa_module_info, eol, user_data):
        if user_data and pa_module_info:
            self.loaded_modules.append(pa_module_info.contents.name)
        return

################### misc

    def pa_ext_stream_restore_delete( self, stream ):
        # Only execute this if module restore is loaded
        if "module-stream-restore" in self.loaded_modules:
            pa_ext_stream_restore_delete(self._context, stream, self._pa_context_success_cb, None)

####### unused

    def load_module_stream_restore(self):
        print "Reloading module-stream-restore "
        pa_context_load_module(self._context, "module-stream-restore", self.module_stream_restore_argument, self._pa_context_index_cb, None)

    # Move a playing stream to a differnt output sink
    def move_sink(self, sink_index, output_name):
        self.__print("move_sink")
        pa_context_move_sink_input_by_name(self._context, sink_index, output_name, self._pa_context_success_cb, None)

################## card profile

    def pulse_set_card_profile(self, index, value):
        operation = pa_context_set_card_profile_by_name(self._context,str(index),str(value) ,  self._null_cb,None)
        pa_operation_unref(operation)
        return  
        
################## volume
    def pulse_mute_stream(self, index):
        self.pulse_sink_input_mute(index, 1)
        return
    def pulse_unmute_stream(self, index):
        self.pulse_sink_input_mute(index, 0)
        return
    def pulse_mute_sink(self, index):
        self.pulse_sink_mute(index, 1)
        return
    def pulse_unmute_sink(self, index):
        self.pulse_sink_mute(index, 0)
        return

    def pulse_sink_input_kill(self, index):
        operation = pa_context_kill_sink_input(self._context,index,  self._null_cb,None)
        pa_operation_unref(operation)
        return

    def pulse_sink_input_mute(self, index, mute):
        operation = pa_context_set_sink_input_mute(self._context,index,mute,  self._null_cb,None)
        pa_operation_unref(operation)
        return

    def pulse_sink_mute(self, index, mute):
        "Mute sink by index"
        operation = pa_context_set_sink_mute_by_index(self._context, index,mute,self._null_cb,None)
        pa_operation_unref(operation)
        return

    def pulse_set_default_sink(self, index):
        operation = pa_context_set_default_sink(self._context, str(index),self._null_cb,None)
        pa_operation_unref(operation)
        return

    def pulse_source_mute(self, index, mute):
        "Mute sink by index"
        operation = pa_context_set_source_mute_by_index(self._context, index,mute,self._null_cb,None)
        pa_operation_unref(operation)
        return

    def pulse_set_default_source(self, index):
        operation = pa_context_set_default_source(self._context, str(index),self._null_cb,None)
        pa_operation_unref(operation)
        return

    def pulse_set_sink_volume(self, index, vol):
        operation = pa_context_set_sink_volume_by_index(self._context,index,vol.toCtypes(), self._null_cb,None)
        pa_operation_unref(operation)
        return

    def pulse_set_source_volume(self, index, vol):
        operation = pa_context_set_source_volume_by_index(self._context, index, vol.toCtypes(), self._null_cb,None)
        pa_operation_unref(operation)
        return

    def pulse_set_sink_input_volume(self, index, vol):
        operation = pa_context_set_sink_input_volume(self._context,index,vol.toCtypes(),self._null_cb,None)
        pa_operation_unref(operation)
        return

    def pulse_move_sink_input(self, index, target):
        operation = pa_context_move_sink_input_by_index(self._context,index, target, self._null_cb, None)
        pa_operation_unref(operation)
        #self.pa_create_monitor_stream_for_sink_input(int(index), self.sink_inputs[float(target)], "", True)
        return

    def pulse_move_source_output(self, index, target):
        operation = pa_context_move_source_output_by_index(self._context,index, target, self._null_cb, None)
        pa_operation_unref(operation)
        #self.pa_create_monitor_stream_for_source(int(index), self.sink_inputs[float(target)], "", True)
        return

    def __print(self, text):
        #print text
        return

#if __name__ == '__main__':
    #c = PulseAudio()

#!/usr/bin/env python
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

import sys
import dbus
import dbus.mainloop.qt

from PyQt4.QtCore import *
import signal

## ps -ef | grep test-dbus  | grep -v grep  | awk '{ print $2 }' | xargs -n 1 kill

class PulseAudioDBus(QObject):


    def start_pulsing(self):
        mainloop = dbus.mainloop.qt.DBusQtMainLoop(set_as_default=True)
        bus = dbus.SessionBus()
        pa_obj  = bus.get_object("org.veromix.pulseaudioservice","/org/veromix/pulseaudio")
        interface = dbus.Interface(pa_obj,dbus_interface="org.veromix.notification")
        interface.connect_to_signal("sink_input_info", self.sink_input_info)
        interface.connect_to_signal("sink_info", self.sink_info)
        interface.connect_to_signal("sink_input_remove", self.sink_input_remove)
        interface.connect_to_signal("sink_remove", self.sink_remove)

    def pa_exit(self):
        pass

    def sink_input_info(self, index,  stream_name, app_name, app_icon):
        self.emit(SIGNAL("sink_input_info(PyQt_PyObject)"), sink )
        #print "sink input signal: " ,  index,  stream_name, app_name, app_icon

    def sink_info(self, index,  stream_name, app_name, app_icon):
        self.emit(SIGNAL("sink_info(PyQt_PyObject)"), sink )
        #print "sink signal: " ,  index,  stream_name, app_name, app_icon

    def sink_input_remove(self, index):
        self.emit(SIGNAL("sink_input_remove(int)"), index )
        #print "sink input remove signal: " ,  index

    def sink_remove(self, index):
        self.emit(SIGNAL("sink_remove(int)"), index )
        #print "sink remove signal: " ,  index


    def pulse_set_sink_input_volume(self, index, vol):
        pass

    def pulse_sink_mute(self, index, mute):
        pass

    def pulse_set_sink_volume(self, index, vol):
        pass

    def pulse_sink_mute(self, index, mute):
        pass

if __name__ == '__main__':
    print 'Entering loop'
    app=QCoreApplication(sys.argv)
    mainloop=dbus.mainloop.qt.DBusQtMainLoop(set_as_default=True)
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    obj = PulseAudioDBus()
    app.exec_()

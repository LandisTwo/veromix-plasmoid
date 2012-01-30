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

from PyQt4.QtCore import *

## FIXME bad name: how is one "channel" of a strereo stream called?
class SinkChannel(QObject):

    def __init__(self, name, volume):
        QObject.__init__(self)
        self.name = name
        self.volume = volume

    def getName(self) :
        return self.name

    def getVolume(self):
        return self.volume

    def printDebug(self):
        print "    <SinkChannel>"
        print  "      <name>", self.name,  "</name>"
        print "       <volume>", self.volume,  "</volume>"
        print "    </SinkChannel>"

class AbstractSink(QObject):

    def __init__(self, pulseaudio, index,   name,  muted  , volume ,  props):
        QObject.__init__(self)
        self.pulse_proxy = pulseaudio
        #self.pa = pulseaudio
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

    def printDebug(self):
        print "<sink type=" +str(type(self))+ ">"
        print  "  <index>", self.index,  "</index>"
        print "  <name>", self.name,  "</name>"
        print "  <mute>", self.mute,  "</mute>"
        print "  <volume>",
        for channel in self.getChannels():
            channel.printDebug()
        print "  </volume>"
        print "  <properties>"
        for key in self.props.keys():
            print "    <" + key + ">", self.props[key],"</" + key + ">"
        print "  </properties>"
        print "</sink>"

    def isMuted(self):
        return self.mute == 1

    def get_monitor_name(self):
        name = "Veromix monitor"
        try:
            name = self.name.encode("ascii")
        except Exception,  e:
            print e
        return name

    ## testing

    def is_sourceoutput(self):
        return False

    def is_sinkoutput(self):
        return False

    def is_sinkinput(self):
        return False

    def is_sink(self):
        return False

    def properties(self):
        return self.props

class SinkInfo(AbstractSink):

    def __init__(self, pulseaudio, index,   name,  muted  , volume ,  props, ports, active_port):
        AbstractSink.__init__(self, pulseaudio, index,   name,  muted  , volume ,  props)
        self.ports=ports
        self.active_port=active_port

    def is_sink(self):
        return True

    def set_volume(self, values):
        self.pulse_proxy.set_sink_volume(self.index, values)

    def toggle_mute(self ):
        if self.isMuted():
            self.pulse_proxy.set_sink_mute(self.index, False)
        else:
            self.pulse_proxy.set_sink_mute(self.index, True)
            
    def set_port(self,portstr):
         self.pulse_proxy.set_sink_port(self.index,portstr)
    
    
    
    def toggle_monitor(self,parent):
        self.pulse_proxy.toggle_monitor_of_sink(self.index, self.get_monitor_name())

    def kill(self):
        pass

    def set_ladspa_sink(self,parameters):
        self.pulse_proxy.set_ladspa_sink(int(self.index), int(self.props["owner_module"]), str(parameters))

    def remove_ladspa_sink(self):
        self.pulse_proxy.remove_ladspa_sink(int(self.props["owner_module"]))


class SinkInputInfo(AbstractSink):

    def is_sinkinput(self):
        return True

    def set_volume(self, values):
        self.pulse_proxy.set_sink_input_volume(self.index, values)

    def toggle_mute(self ):
        if self.isMuted():
            self.pulse_proxy.set_sink_input_mute(self.index, False)
        else:
            self.pulse_proxy.set_sink_input_mute(self.index, True)

    def toggle_monitor(self,parent):
        self.pulse_proxy.toggle_monitor_of_sinkinput(self.index, parent,self.get_monitor_name())

    def kill(self):
        self.pulse_proxy.sink_input_kill(self.index)

class SourceInfo(AbstractSink):

    def __init__(self, pulseaudio, index,   name,  muted  , volume ,  props, ports, active_port):
        AbstractSink.__init__(self, pulseaudio, index,   name,  muted  , volume ,  props)
        self.ports=ports
        self.active_port=active_port

    def is_sinkoutput(self):
        return True

    def set_volume(self, values):
        self.pulse_proxy.set_source_volume(self.index, values)

    def toggle_mute(self ):
        if self.isMuted():
            self.pulse_proxy.set_source_mute(self.index, False)
        else:
            self.pulse_proxy.set_source_mute(self.index, True)
            
    def set_port(self,portstr):
         self.pulse_proxy.set_source_port(self.index,portstr)
         
    def toggle_monitor(self,parent):
        self.pulse_proxy.toggle_monitor_of_source(self.index, self.get_monitor_name())

    def kill(self):
        pass

class SourceOutputInfo(AbstractSink):

    def is_sourceoutput(self):
        return True

    def set_volume(self, values):
        pass

    def toggle_mute(self ):
        pass

    def kill(self):
        pass

    def toggle_monitor(self,parent):
        pass


class CardProfile:
    def __init__(self, name, properties):
        self.name = name
        self.properties = properties
        self.description = properties["description"]
        # FIXME other values

    def printDebug(self):
        print "<CardProfile>"
        print "  <name>", self.name, "</name>"
        print "  <properties>"
        for key in self.properties.keys():
            print "    <" + key + ">", self.properties[key],"</" + key + ">"
        print "  </properties>"
        print "</CardProfile>"

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

    def get_property(self,key):
        if self.properties == None:
            return ""
        if key in self.properties.keys():
            return self.properties[key]
        return ""

    def get_description(self):
        return self.get_property("device.description")

    def get_profiles(self):
        return self.profiles

    def get_active_profile(self):
        for profile in self.card_profiles():
            if self.active_profile_name == profile.name:
                return profile
        return None

    def get_active_profile_name(self):
        return self.active_profile_name

    def printDebug(self):
        print "<CardInfo>"
        print  "  <index>", self.index,  "</index>"
        print "  <name>", self.name, "</name>"
        print "  <properties>"
        for key in self.properties.keys():
            print "    <" + key + ">", self.properties[key],"</" + key + ">"
        print "  </properties>"
        print "</CardInfo>"
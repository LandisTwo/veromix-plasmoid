# -*- coding: utf-8 -*-
# Copyright (C) 2010-2012 Nik Lutz <nik.lutz@gmail.com>
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

import gettext
i18n = gettext.gettext

try:
    import html
except:
    class html:
        @staticmethod
        def escape(arg):
            return str(arg)

## FIXME bad name: how is one "channel" of a strereo stream called?
class SinkChannel():

    def __init__(self, name, volume):
        self.name = name
        self.volume = volume

    def get_name(self) :
        return self.name

    def get_volume(self):
        return self.volume

    def printDebug(self):
        print("    <SinkChannel>")
        print("      <name>" + self.name + "</name>")
        print("       <volume>" + self.volume + "</volume>")
        print("    </SinkChannel>")

class AbstractSink():
    # FIXME KDE
    DEFAULT_ICON = "audio-x-generic-symbolic"

    def __init__(self, pulseaudio, index, name, muted, volume, props):
        self.pulse_proxy = pulseaudio
        self.index =  index
        self.name =   name
        self.mute  =   muted
        self. volume  =   volume
        self.props = props
        self._update_nice_values(pulseaudio.veromix)

    def is_default(self):
        return False

    def get_index(self):
        return int(self.index)

    def get_name(self) :
        return self.name

    def toggle_mute(self ):
        pass

    def step_volume_by(self, STEP, up):
        vol = self.get_volume()
        if up:
            vol = vol + STEP
        else:
            vol = vol - STEP
        if vol < 0:
            vol = 0
        if vol > 100: # FIXME self.get_max_volume_value():
            vol = 100 #self.get_max_volume_value()
        self.set_volume(self.volumeDiffFor(vol))

    def set_volume(self, values):
        pass

    def get_volume(self):
        val =0
        for t in list(self.volume.keys()):
            val += list(self.volume[t].values())[0]
        return int(val/ len(list(self.volume.keys())))

    def getChannels(self):
        channels = []
        for key in list(self.volume.keys()):
            t = self.volume[key]
            name = list(t.keys())[0]
            vol = list(t.values())[0]
            channels.append(SinkChannel(name,vol))
        return channels

    def volumeDiffFor(self, value):
        vol = []
        diff = self.get_volume() - value
        for key in list(self.volume.keys()):
            value = list(self.volume[key].values())[0] - diff
            if value < 0:
                value = 0
            vol.append(value )
        return vol

    def printDebug(self):
        print("<sink type=" +str(type(self))+ ">")
        print("  <index>" + self.index + "</index>")
        print("  <name>" + self.name + "</name>")
        print("  <mute>" + self.mute +  "</mute>")
        print("  <volume>")
        for channel in self.getChannels():
            channel.printDebug()
        print("  </volume>")
        print("  <properties>")
        for key in list(self.props.keys()):
            print("    <" + key + ">", self.props[key],"</" + key + ">")
        print("  </properties>")
        print("</sink>")

    def isMuted(self):
        # FIXME
        return self.is_muted()

    def is_muted(self):
        return self.mute == 1

    def get_monitor_name(self):
        name = "Veromix monitor"
        try:
            name = self.name.encode("ascii")
        except Exception as  e:
            print(e)
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

    def _update_nice_values(self, veromix=None):
        self._nice_text =  ""
        self._nice_title = self.name
        self._nice_icon = self.DEFAULT_ICON

    def get_nice_text(self):
        return html.escape(self._nice_text)

    def get_nice_title(self):
        return html.escape(self._nice_title)

    def get_nice_icon(self):
        return self._nice_icon

    def get_nice_title_and_name(self):
        return "<b>" + self.get_nice_title() + "</b> " + self.get_nice_text()

    def is_default_sink(self):
        return False

    def get_output_index(self):
        return int(self.get_index())

    def get_owner_module(self):
         if "owner_module" in self.props:
            return self.props["owner_module"]
         return None

class SinkInfo(AbstractSink):
    # FIXME KDE
    DEFAULT_ICON = "audio-card-symbolic"

    def __init__(self, pulseaudio, index, name, muted, volume, props, ports, active_port):
        AbstractSink.__init__(self, pulseaudio, index, name, muted, volume, props)
        self.ports=ports
        self.active_port=active_port

    def is_sink(self):
        return True

    def be_default_sink(self):
        self.pulse_proxy.set_default_sink(self.name)

    def is_default(self):
        if "isdefault" in self.props:
            return self.props["isdefault"] == "True"
        return False

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

    def remove_combined_sink(self):
        self.pulse_proxy.remove_combined_sink(int(self.props["owner_module"]))

    def is_default_sink(self):
        if "isdefault" in self.props:
            return self.props["isdefault"] == "True"
        return False

    def _update_nice_values(self, veromix=None):
        self._nice_text =  ""
        self._nice_title = self.name
        self._nice_icon = self.DEFAULT_ICON
        text = ""
        try:
            self._nice_title = self.props["device_name"]
        except:
            pass

    def move_sink_input(self, target_sink):
        self.pulse_proxy.move_sink_input(int(target_sink), int(self.get_index()))

    def is_ladspa_sink(self):
        return "device.ladspa.module" in sink.properties().keys()
        # return self.props["device.ladspa.module"] == 


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

    def _update_nice_values(self, veromix=None):
        text =  self.name
        bold = self.props["app"]
        iconname = None

        if self.props["app_icon"] != "None":
            iconname = self.props["app_icon"]
        ## FIXME KDE
        #if iconname == None and  self.props["app"] != "None":
            #iconname = self.veromix.query_application(self.props["app"])
        if bold == "knotify":
            bold = i18n("Event Sounds")
            text = ""
            iconname = 'dialog-information'
        if bold == "npviewer.bin" or bold == "plugin-container":
            bold = i18n("Flash Player")
            text = ""
            iconname = 'flash'
        if bold == "chromium-browser":
            bold = i18n("Chromium Browser")
            text = ""
        if bold == "Skype":
            if text == "Event Sound":
                text = i18n("Event Sound")
            if text == "Output":
                text = i18n("Voice Output")

        if veromix:
            if text == "LADSPA Stream" or ("media.name" in self.props.keys() and self.props["media.name"] == "LADSPA Stream"):
                for sink in veromix.get_sink_widgets():
                    if sink.pa_sink.props["owner_module"] == self.props["owner_module"]:
                        bold = sink.pa_sink.props["device.ladspa.name"]
                        text = ""
                        iconname = sink.pa_sink.props["device.icon_name"]

        # FIXME
        if bold in ["", "None", None]:
            bold = text
            text = ""

        if text in ["None", None]:
            text = ""

        if iconname in ["", "None", None]:
            iconname = self.DEFAULT_ICON # FIXME "mixer-pcm"
        self._nice_text = text
        self._nice_title = bold
        self._nice_icon = iconname

    def get_output_index(self):
        return int(self.props["sink"])

class SourceInfo(AbstractSink):
    DEFAULT_ICON = "audio-input-microphone-symbolic"

    def __init__(self, pulseaudio, index, name, muted, volume, props, ports, active_port):
        AbstractSink.__init__(self, pulseaudio, index, name, muted, volume, props)
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

    def _update_nice_values(self, veromix=None):
        self._nice_text =  ""
        self._nice_title = self.name
        self._nice_icon = self.DEFAULT_ICON
        if "description" in self.props.keys():
            self._nice_title = self.props["description"]
#            self._nice_text = self.name

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


    def get_volume(self):
        return 0

    def getChannels(self):
        return []

    def _update_nice_values(self, veromix=None):
        self._nice_text =  ""
        self._nice_title = self.name
        self._nice_icon = self.DEFAULT_ICON
        if "description" in self.props.keys():
            self._nice_title = self.props["description"]
            self._nice_text = self.name

        if self.name.find("ALSA") == 0 and "application.process.binary" in self.props.keys():
            self._nice_title = self.props[ "application.process.binary"]
            self._nice_text =  self.props[ "application.name"]

        if "application.icon_name" in self.props.keys():
            self._nice_icon = self.props["application.icon_name"]

        if veromix:
            if iconname == None and  "app" in self.props.keys():
                self._nice_icon = veromix.query_application(self.props["app"])

        if self._nice_icon is None and self._nice_title == "plugin-container":
            self._nice_icon = 'flash'

class CardProfile:
    def __init__(self, name, properties):
        self.name = name
        self.properties = properties
        self.description = properties["description"]
        # FIXME other values

    def printDebug(self):
        print("<CardProfile>")
        print("  <name>", self.name, "</name>")
        print("  <properties>")
        for key in list(self.properties.keys()):
            print("    <" + key + ">", self.properties[key],"</" + key + ">")
        print("  </properties>")
        print("</CardProfile>")

class CardInfo:
    def __init__(self, index, name, properties, active_profile_name, profiles_dict):
         self.index = index
         self.name = name
         self.properties = properties
         self.active_profile_name = active_profile_name
         self.profiles_dict = profiles_dict
         self.profiles = []
         for key in list(self.profiles_dict.keys()):
             self.profiles.append(CardProfile(key, self.profiles_dict[key] ))

    def get_property(self,key):
        if self.properties == None:
            return ""
        if key in list(self.properties.keys()):
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
        print("<CardInfo>")
        print("  <index>", self.index,  "</index>")
        print("  <name>", self.name, "</name>")
        print("  <properties>")
        for key in list(self.properties.keys()):
            print("    <" + key + ">", self.properties[key],"</" + key + ">")
        print("  </properties>")
        print("</CardInfo>")
        
class ModuleInfo:

    def __init__(self, index, name, argument, n_used, auto_unload):
        self.index = index
        self.name = name
        self.argument = argument
        self.n_used = n_used
        self.auto_unload = auto_unload


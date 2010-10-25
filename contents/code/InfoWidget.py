# -*- coding: utf-8 -*-
# copyright 2009  Nik Lutz
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

from PyKDE4.plasma import Plasma
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyKDE4.kdeui import *


class SinkInfoWidget(QGraphicsWidget):
    
    def __init__(self, veromix, sink):
        QGraphicsWidget.__init__(self)
        self.veromix = veromix
        self.sink = sink
        self.text = ""
        self.INFO_ICON = "hwinfo"
        self.init()        
        
    def init(self):
        self.init_arrangement()
        self.create_text_area()
        self.create_switcher()
        self.compose_arrangement()
  
    def compose_arrangement(self):
        self.layout.addItem(self.switcher)
        self.layout.addStretch()
        self.layout.addItem(self.button)
  
    def init_arrangement(self):        
        self.layout = QGraphicsLinearLayout(Qt.Horizontal)       
        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)
        
    def create_text_area(self):
        self.button = Plasma.PushButton()
        self.button.setIcon(KIcon(self.INFO_ICON))
        self.button.clicked.connect(self.on_show_message)
        
    def create_switcher(self):
        self.switcher = Plasma.CheckBox()
        self.switcher.toggled.connect(self.on_change_switcher)
        self.switcher.setText("Default")
        self.switcher.setMinimumSize(self.switcher.preferredSize())
        
    def update_with_info(self, info):
        self.text = ""
        values = info.props.keys()
        values.sort()
        for key in values:
            self.text += "<b>" + key + ":</b> "+ info.props[key]+"<br/>"  
        self.updateOutputSwitcher()

    def on_change_switcher(self,boolean):
        if boolean:
            self.sink.pa.set_default_sink(self.sink.index )        
    
    def updateOutputSwitcher(self):
        self.switcher.nativeWidget().setChecked(self.sink.pa_sink.props["isdefault"] == "True")
    
    def on_show_message(self):
        if self.veromix.applet.isPopupShowing():
           self.veromix.applet.hidePopup()     
        self.veromix.showMessage(KIcon(self.INFO_ICON), self.text)
        
class SinkInputInfoWidget(SinkInfoWidget):
    
    def __init__(self, veromix, sink):
        self.kill_text = "Terminate this sink"
        self.veromix = veromix
        self.sink = sink
        SinkInfoWidget.__init__(self, veromix, sink)        
        self.veromix.sinkOutputChanged.connect(self.updateOutputSwitcher)
        

    def compose_arrangement(self):
        self.layout.addStretch()
        self.layout.addItem(self.switcher)
        self.layout.addItem(self.button)

    def create_switcher(self):
        self.switcher = Plasma.ComboBox()
        self.switcher.activated.connect(self.on_change_switcher)

    def keys_for_string(self,  string, values, props):
        text = ""
        rem = []
        for key in values:
            if key.startswith(string):
                k =  key.replace(string, "").lstrip(".").replace(".", " ")
                text += "<b>" + k + ":</b> "+ props[key] +"<br/>"                
                rem.append(key)
        for x in rem:
            del values[values.index(x)]
        return text
        
    def updateOutputSwitcher(self):
        if self.switcher :
            pass
        else:
            return 0
        self.switcher.clear()
        outputs =  self.veromix.getSinkOutputs()
        ## fill combobox
        for output in outputs:
            self.switcher.addItem(output.app)
        self.switcher.addItem(self.kill_text)
        ## set current selection
        for output in outputs:
            if int(output.index) == int(self.sink.getOutputIndex()) :
                self.switcher.nativeWidget().setCurrentIndex(self.veromix.getSinkOutputs().index(output))
        self.switcher.setMinimumSize(self.switcher.preferredSize())
        #self.switcher.adjustSize()
        
    def on_change_switcher(self,event):
        if self.switcher.text() == self.kill_text:
            self.sink.sink_input_kill()
            return 0
        # search ouputs for text, and move sink_input
        for output in self.veromix.getSinkOutputs():
            if self.switcher.text() == output.app: 
                self.sink.pa.move_sink_input(self.sink.index, int(output.index))
                return 0

    def update_with_info3(self, info):
        #self.name =   name
        #self.mute  =   muted
        #self. volume  =   volume
        #self.client_index = client_index  
        #self.client_name = client_name
        #self.props = props        
        
        values = info.props.keys()      
        
        blacklist = ["app", 
                                "application.process.machine_id" ,
                                "application.process.session_id",
                                "application.process.user" ,
                                "application.icon_name" ,
                                "module-stream-restore.id",
                                #"application.process.host", 
                                "application.language",
                                "owner_module",
                                "name",
                                "sink",
                                "index",
                                "client_id",
                                "native-protocol.version" ,
                                "window.x11.display",
                                "channel_map",
                                "app_icon",
                                "sink_usec",
                                "buffer_usec",
                                "sample_spec"]
        for b in blacklist:
            if b in values:
                del values[values.index(b)]        
        values.sort()       
        
        text = self.keys_for_string("application", values,info.props)
        text += "<br/>" 
        text += self.keys_for_string("media", values,info.props)     
        #self.text_area.setText(text)
        text += "<br/>" 
        
        for key in values:
            text += "<b>" + key + ":</b> "+ info.props[key] +"<br/>"
        #self.text_area.setText(text)
        self.updateOutputSwitcher()
        
        
    ## input info
        #('name', c_char_p),
    #('index', c_uint32),
    #('description', c_char_p),
    #('sample_spec', pa_sample_spec),
    #('channel_map', pa_channel_map),
    #('owner_module', c_uint32),
    #('volume', pa_cvolume),
    #('mute', c_int),
    #('monitor_source', c_uint32),
    #('monitor_source_name', c_char_p),
    #('latency', pa_usec_t),
    #('driver', c_char_p),
    #('flags', pa_sink_flags_t),
    #("proplist",        POINTER(c_int)),
    
    #class struct_pa_sink_input_info(Structure):
    #__slots__ = [
        #'index',
        #'name',
        #'owner_module',
        #'client',
        #'sink',
        #'sample_spec',
        #'channel_map',
        #'volume',
        #'buffer_usec',
        #'sink_usec',
        #'resample_method',
        #'driver',
        #'mute',
        #'proplist',
        #'monitor_index',
    
    #class struct_pa_client_info(Structure):
    #__slots__ = [
        #'index',
        #'name',
        #'owner_module',
        #'driver',
        #'proplist'
    
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

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyKDE4.kdeui import *
from PyKDE4.plasma import Plasma

import signal, os, datetime
from LabelSlider import *
from InfoWidget import *
from Channel import *
from MuteButton  import *
from ClickableMeter import *

class SourceOutputUI( Channel ):
    def __init__(self , parent):
        self.mouse_pressed = False
        Channel.__init__(self, parent)         
        
    def createMute(self):
        self.mute = InputMuteButton(self)
        self.mute.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum,True) )
        self.connect(self.mute, SIGNAL("clicked()"), self.on_mute_cb  )      
        self.mute.setBigIconName("audio-input-microphone.png")
    
    def createSlider(self): 
        Channel.createSlider(self)
        self.slider.hideSlider()

    def update_with_info(self,info):
        self.update_essentials(info)
        #info.printDebug()
        now = datetime.datetime.now()
        #if (now - self.plasma_timestamp).seconds > 1 :
            #self.update_pulse_timestamp()
            #self.slider.setValue(info.getVolume())
        self._set_values(info)   
        if self.extended_panel:
            self.extended_panel.update_with_info(info)
            
    def update_label(self):
        text =  ""
        bold = self.pa_sink.name 
        if "description" in self.pa_sink.props.keys():
            bold = self.pa_sink.props["description"]
            text = self.pa_sink.name

        if self.name.find("ALSA") == 0 and "application.process.binary" in self.pa_sink.props.keys(): 
            bold = self.pa_sink.props[ "application.process.binary"]
            text =  self.pa_sink.props[ "application.name"]

        if self.slider:
            self.slider.setText(text)
            #self.slider.setBoldText(bold+" "+str(self.index) + " "+  str(self.sortOrderIndex) + " "+str( self.sinkIndexFor(self.getOutputIndex())) + " "+str(self.getOutputIndex()))
            self.slider.setBoldText(bold)
        if "application.icon_name" in self.pa_sink.props.keys():
            iconname = self.pa_sink.props["application.icon_name"]
        if iconname == None and  "app" in self.pa_sink.props.keys():
            iconname = self.veromix.query_application(self.pa_sink.props["app"])
            
        if iconname is None and bold == "plugin-container":
            iconname = 'flash'
        
        if iconname :
            self.mute.setBigIconName(iconname)
            self.updateIcon()            
                
    def getOutputIndex(self):
        try:
            return int(str(self.pa_sink.props["source"]))           
        except:
            return 0 
  
    def updateSortOrderIndex(self):
        if self.pa_sink:
            self.sortOrderIndex =  self.sinkIndexFor(int(self.getOutputIndex())) +  self.index

    def on_slider_cb(self, value):
        pass

    def on_update_meter(self, index, value, number_of_sinks):
        if self.getOutputIndex() == index:
            self.meter.setValue(value)

### Drag and Drop

    def mousePressEvent(self, event):
        self.mouse_pressed = True

    def mouseReleaseEvent(self, event):
        self.mouse_pressed = False

    def mouseMoveEvent(self,e):
        if self.mouse_pressed :
            self.startDrag(e)

    def startDrag(self,event):
        drag = QDrag(event.widget())
        mimedata = QMimeData()
        liste = []
        liste.append(QUrl( "veromix://source_output_index:"+str(int(self.index)) ))
        mimedata.setUrls(liste)
        drag.setMimeData(mimedata)
        #drag.setHotSpot(event.pos() - self.rect().topLeft())
        dropAction = drag.start(Qt.MoveAction)

    def isSinkOutput(self):
        return False    
        
    def isSourceOutput(self):
        return True
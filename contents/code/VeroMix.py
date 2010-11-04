# -*- coding: utf-8 -*-
# copyright 2010  Nik Lutz nik.lutz@gmail.com
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

import sys, os, commands, time
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyKDE4.plasma import Plasma
from PyKDE4 import plasmascript
from PyKDE4.kdeui import *
from PyKDE4.kdecore import *
from PyKDE4.kdecore import *
from PyKDE4.plasma import * 

import signal, os, datetime
from SinkUI import *
from SinkInputUI import *
from LabelSlider import *
from PulseAudioProxy import *
from SortedLayout import *
from SourceUI import *
from SourceOutputUI import *
from NowPlaying import * 

class VeroMix(QGraphicsWidget):
    sinkOutputChanged = pyqtSignal()
    
    def __init__(self,parent):
        QGraphicsWidget.__init__(self)
        self.applet = parent        
        self.sinks = {} 
        self.sources = {} 
        self.outputs = {}
        self.mouse_is_over = False
        self.pa = None

    def init(self):  
        self.setAcceptsHoverEvents (True)
        self.layout = QGraphicsLinearLayout(Qt.Vertical, self)
        self.layout.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)) 
        
        self.scroller = Plasma.ScrollWidget(self)
        self.scroller.setMinimumSize(120,90)
        self.layout.addItem(self.scroller)
        
        self.source_panel = QGraphicsWidget()
        self.sink_panel = QGraphicsWidget()
        
        useTabs = False
        if useTabs:
            self.scrolled_panel = Plasma.TabBar()
            self.scrolled_panel.addTab("Play", self.sink_panel)
            self.scrolled_panel.addTab("Record", self.source_panel)
        else:
            self.scrolled_panel = QGraphicsWidget()
            self.scrolled_panel_layout = QGraphicsLinearLayout(Qt.Vertical)
            self.scrolled_panel.setLayout(self.scrolled_panel_layout)
            self.scrolled_panel_layout.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)) 
            self.scrolled_panel_layout.addItem(self.source_panel)
            self.scrolled_panel_layout.addItem(self.sink_panel)            
            self.scrolled_panel_layout.setContentsMargins(0,0,0,6)
        self.scroller.setWidget(self.scrolled_panel)        
        
        #button = Plasma.PushButton()
        #button.setIcon(KIcon("veromix-plasmoid-128"))
        #self.scrolled_panel_layout.addItem(button)
        
        
        self.source_panel_layout = SortedLayout(Qt.Vertical, False)
        self.source_panel.setLayout(self.source_panel_layout)
        self.source_panel_layout.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)) 
        
        self.sink_panel_layout = SortedLayout(Qt.Vertical, False)
        self.sink_panel.setLayout(self.sink_panel_layout)
        self.sink_panel_layout.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)) 
        
        self.layout.setContentsMargins(0,0,0,0)
        
        self.source_panel_layout.setContentsMargins(0,0,0,12)
        self.sink_panel_layout.setContentsMargins(0,0,0,0)
    
        #QTimer.singleShot(4000, self.start_pa)
        #self.restore = False
        self.start_pa()   
        self.startNowPlaying()

    def setSourcesPanelVisible(self, aBoolean):
        #if self.applet.isPopupShowing():
        if aBoolean :
            self.source_panel.show()
            self.scrolled_panel_layout.insertItem(0, self.source_panel)
        else:
            self.source_panel.hide()
            self.scrolled_panel_layout.removeItem(self.source_panel)
            
    def start_pa(self):
        try:
            self.pa = PulseAudio(self)
        except:
            self.showMessage(KIcon("script-error"), "There is a problem with the backgroud-service. \
                                                        <ul> \
                                                        <li>If you just upgraded try killing the process named: VeromixServiceMain.py and relaunch this plasmoid</li> \
                                                        <li>If you don't know how to do that consider rebooting</li></ul>")
            return 
        self.connect(self.pa, SIGNAL("on_sink_input_info(PyQt_PyObject)"), self.on_sink_input_info)
        self.connect(self.pa, SIGNAL("on_sink_info(PyQt_PyObject)"), self.on_sink_info)
        self.connect(self.pa, SIGNAL("on_source_output_info(PyQt_PyObject)"), self.on_source_output_info)
        self.connect(self.pa, SIGNAL("on_source_info(PyQt_PyObject)"), self.on_source_info)
        
        self.connect(self.pa, SIGNAL("on_sink_remove(int)"), self.on_remove_sink)
        self.connect(self.pa, SIGNAL("on_sink_input_remove(int)"), self.on_remove_sink_input)
        self.connect(self.pa, SIGNAL("on_source_remove(int)"), self.on_remove_source)
        self.connect(self.pa, SIGNAL("on_source_output_remove(int)"), self.on_remove_source_output)
        
        self.connect(self.pa, SIGNAL("on_volume_meter_sink_input(int, float )"), self.on_volume_meter_sink_input)
        self.connect(self.pa, SIGNAL("on_volume_meter_source(int, float )"), self.on_volume_meter_source)
        self.pa.requestInfo()
 
    def startNowPlaying(self):
        print "start now p"
        self.applet.nowplaying_player_added.connect(self.on_nowplaying_added)
        self.applet.nowplaying_player_removed.connect(self.on_nowplaying_removed)
        
    def on_nowplaying_added(self, name, controller):
        print "on_nowplaying_added", name
        self.layout.addItem(NowPlaying(self, controller ))

    def on_nowplaying_removed(self, name):
        print "on_nowplaying_added", name

    def getPulseAudio(self):
        return self.pa       
   
    def check_geometries(self):
        self.check_ItemOrdering()
        count = 0
        for source in self.sources.values():
            if source.isSourceOutput():
                count += 1
        self.setSourcesPanelVisible( count > 0 )
        self.sink_panel.adjustSize()
        self.source_panel.adjustSize()
        self.scrolled_panel.adjustSize()
        if self.applet.formFactor()  == Plasma.Planar:
            pass
        else:
            #pass
            #print "formfactor" = 
            #self.setSizePolicy(QSizePolicy.Preferred)
            self.setMinimumHeight(self.scrolled_panel.preferredSize().height())
            self.setMaximumHeight(self.scrolled_panel.preferredSize().height())
        #self.updateGeometry()
       
    def check_ItemOrdering(self):
        self.sink_panel_layout.check_ItemOrdering(self.sinks) 
        self.source_panel_layout.check_ItemOrdering(self.sources)   
    
    def on_sink_input_info(self,  sink):
        ## SinkInputs and Sinks/outputs can have the same index .. 
        if  (sink.index+1000) in self.sinks :
            self.sinks[sink.index+1000].update_with_info(sink)
            self.check_ItemOrdering()        
            return 
        widget = InputSinkUI(  self)
        widget.update_with_info(sink)
        self.add_sink_to_layout(widget)
        self.sinks[sink.index + 1000 ] = widget
        self.check_geometries()

    def on_remove_sink_input(self, index):
        ## SinkInputs and Sinks/outputs can have the same index .. 
        if (index +1000 ) in self.sinks :
            self.remove_sink_from_layout(self.sinks[index+1000])
            self.sinks[index+1000].deleteLater()
            del self.sinks[index+1000]
        self.check_geometries()
        
    def on_source_output_info(self,  sink):
        if  (sink.index-1000) in self.sources :
            self.sources[sink.index-1000].update_with_info(sink)
            self.check_ItemOrdering()        
            return 
        # FIXME sliders want to be visible when added, else we get a crash
        self.setSourcesPanelVisible(True)
        widget = SourceOutputUI( self)
        widget.update_with_info(sink)
        self.add_source_to_layout(widget)
        self.sources[sink.index - 1000 ] = widget
        self.check_geometries()
   
    def on_remove_source_output(self, index):
        if (index -1000 ) in self.sources :
            # FIXME sliders want to be visible when added, else we get a crash
            self.setSourcesPanelVisible(True)
            self.remove_source_from_layout(self.sources[index-1000])
            self.sources[index-1000].deleteLater()
            del self.sources[index-1000]
            self.check_geometries()

    def on_source_info(self,  sink):
        if  sink.index in self.sources :
            self.sources[sink.index].update_with_info(sink)
            self.check_ItemOrdering()        
            return 
        # FIXME sliders want to be visible when added, else we get a crash
        self.setSourcesPanelVisible(True)
        widget = SourceUI( self)
        widget.update_with_info(sink)
        self.add_source_to_layout(widget)
        self.sources[sink.index  ] = widget
        self.check_geometries()

    def on_remove_source(self, index):        
        if index  in self.sources :
            # FIXME sliders want to be visible when added, else we get a crash
            self.setSourcesPanelVisible(True)   
            self.remove_source_from_layout(self.sources[index])
            self.sources[index].deleteLater()
            del self.sources[index]
            self.check_geometries()      

    def on_sink_info(self,sink):
        if  sink.index in self.sinks :
            self.sinks[sink.index].update_with_info(sink)
            self.check_ItemOrdering()
            return 
        widget = SinkUI(self)
        widget.update_with_info(sink)
        widget.muteInfo.connect(self.updateIcon)
        self.add_sink_to_layout(widget)
        self.sinks[sink.index] = widget
        self.check_geometries()
        self.sinkOutputChanged.emit()

    def on_remove_sink(self, index):
        for i in self.sinks.keys() :
            if i == index:
                self.remove_sink_from_layout(self.sinks[index])
                self.sinks[index].deleteLater()
                del self.sinks[index]
        self.check_geometries()
        self.sinkOutputChanged.emit()

    def add_sink_to_layout(self, widget):    
        self.sink_panel_layout.addItem(widget)
    
    def add_source_to_layout(self, widget):    
        self.source_panel_layout.addItem(widget)
         
    def remove_sink_from_layout(self, widget):
        self.sink_panel_layout.removeItem(widget)
    
    def remove_source_from_layout(self, widget):
        self.source_panel_layout.removeItem(widget)
    
    def on_volume_meter_sink_input(self, index, level):
        if not self.mouse_is_over:
          return 
        for sink in self.sinks:
            self.sinks[sink].on_update_meter(index,int(level), len(self.sinks))
  
    def on_volume_meter_source(self, index, level):
        if not self.mouse_is_over:
          return 
        for sink in self.sources:
            self.sources[sink].on_update_meter(index,int(level), len(self.sources))
     
    def getSinkOutputs(self):
        toreturn = []
        for index in self.sinks.keys() :
            if self.sinks[index].isSinkOutput():
                toreturn.append(self.sinks[index])
        return toreturn
                
     
    def hoverMoveEvent(self,event):
        self.mouse_is_over = True
        self.trigger_volume_updates()

    def hoverLeaveEvent(self,event):
        self.mouse_is_over = False
    
    def trigger_volume_updates(self):
        if self.mouse_is_over :
            self.pa.trigger_volume_updates()
            QTimer.singleShot(2000, self.trigger_volume_updates)            
            
    def updateIcon(self, muted):
        if muted:
            self.applet.setPopupIcon(self.applet.volume_muted)
        else:
            self.applet.setPopupIcon(self.applet.volume_high)
        
    def resizeEvent(self, e):
        self.emit(SIGNAL("resized()"))
        
    def query_application(self, needle):
        return self.applet.query_application(needle)
        
    def showMessage(self, icon, message):
        self.applet.showMessage(icon, message, Plasma.ButtonOk)

    def getDefaultSink(self):
        for sink in self.sinks.values():
            if sink.isDefaultSink():
                return sink
        for sink in self.sinks():
            if sink.isSinkOutput():
                return sink
        return None

    def on_toggle_mute(self):
        sink = self.getDefaultSink()
        if sink != None:
            sink.on_mute_cb()

    def on_step_volume(self, up):
        sink = self.getDefaultSink()
        if sink != None:
            sink.on_step_volume(up)

    def doExit(self):
        for i in self.sinks.values():
            # if a slider is not visible, plasmoidviewer crashes if the slider is not removed before exit... (dont ask me)
            i.removeSlider()
        for i in self.sources.values():
            # if a slider is not visible, plasmoidviewer crashes if the slider is not removed before exit... (dont ask me)
            i.removeSlider()
        
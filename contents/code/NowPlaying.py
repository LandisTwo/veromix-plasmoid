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
import dbus

import signal, os, datetime
from LabelSlider import LabelSlider
from LabelSlider import Label
from Channel import Channel
from MuteButton  import *

class NowPlaying( Channel ):
    Stopped, Playing, Paused, NA = range(4)  
    
    def __init__(self,veromix, controller):
        self.controller = controller
        Channel.__init__(self, veromix)  
        self.index = -1
        self.state = NowPlaying.NA
        self.position = 0
        self.length = 0  
        self.artwork = ""
        self.cover_string = ""
        self.setEnabledBorders (Plasma.FrameSvg.LeftBorder)
        self.setEnabledBorders (Plasma.FrameSvg.RightBorder)
        self.setEnabledBorders (Plasma.FrameSvg.TopBorder)
        
    def initArrangement(self):        
        #self.setContentsMargins(6,3,6,0)
        #self.layout.setContentsMargins(6,3,6,10)
        self.svg_path = self.veromix.applet.package().filePath('images', 'buttons.svgz')
        self.createMiddle()      
        self.createSlider()
        self.createPlayControlsBar()
        self.createPanel()
        self.createPrev()
        self.createPlayPause()
        self.createNext() 
        self.createPositionLabel()

    def composeArrangement(self):
        self.composeArrangement1()
        
    def composeArrangement1(self):
        self.layout.addItem(self.panel)
        self.controlsbar_layout.addItem(self.prev)
        self.controlsbar_layout.addStretch()
        self.controlsbar_layout.addItem(self.play)
        self.controlsbar_layout.addStretch()
        self.controlsbar_layout.addItem(self.next)
        
        self.middle_layout.setSpacing(0)
        self.middle_layout.addStretch()        
        self.middle_layout.addItem(self.positionLabel)
        self.middle_layout.addItem(self.controlsbar)
        self.panel_layout.addStretch()
        self.panel_layout.addItem(self.middle)    
        self.panel_layout.addStretch()
        self.CONTROLSBAR_SIZE = 112
        self.middle.setPreferredSize(QSizeF(self.CONTROLSBAR_SIZE,self.CONTROLSBAR_SIZE))
        self.middle.setMaximumSize(QSizeF(self.CONTROLSBAR_SIZE,self.CONTROLSBAR_SIZE))

    def composeArrangement2(self):
        self.layout.addItem(self.middle)
        self.layout.addItem(self.panel)
        self.panel_layout.addItem(self.prev)
        self.panel_layout.addItem(self.play)
        self.panel_layout.addItem(self.next)
        #self.panel_layout.addItem(self.slider)
        self.CONTROLSBAR_SIZE = 90
        self.middle.setPreferredSize(QSizeF(self.CONTROLSBAR_SIZE,self.CONTROLSBAR_SIZE))
        self.middle.setMaximumSize(QSizeF(self.CONTROLSBAR_SIZE,self.CONTROLSBAR_SIZE))

    def update_with_info(self, info):                
        data = info
        if self.useDbusWorkaround():
            data = self.getDbusInfo()
        self.updateState(data)
        self.updatePosition(data)
        self.updateCover(data)        
        self.updateSortOrderIndex()
        
    def updateState(self,data):
        state = self.state
        if QString('State') in data:
            if data[QString('State')] == u'playing':
                state = NowPlaying.Playing
            else:
                state = NowPlaying.Paused
        if self.state != state:
            self.state = state
            if self.state == NowPlaying.Playing:
                self.play.setSvg(self.svg_path, "pause-normal")     
            else:
                self.play.setSvg(self.svg_path, "play-normal")     
        
    def getPauseIcon(self):
        name = self.get_application_name()
        app = self.veromix.query_application(str(name))
        if app == None:
            return name
        return app
        
    def updateCover(self,data):      
        if self.state == NowPlaying.Paused  :
            if self.artwork != None:
                self.artwork = None
                self.middle.setIcon(KIcon(self.getPauseIcon()))
            return 
        if QString('Artwork') in data:
            val = data[QString('Artwork')]
            if self.artwork !=  val:
                self.artwork = val
                if val == None:
                    self.middle.setIcon(KIcon(self.getPauseIcon()))
                else:
                    self.middle.setIcon(QIcon(QPixmap(val)))
                    
    def updatePosition(self, data):
        if QString('Position') in data:
            v = data[QString('Position')]
            if v != self.position:               
                self.position = v
                pos_str = ( '%d:%02d' % (v / 60, v % 60))
                self.positionLabel.setBoldText(pos_str)            
        if QString('Length') in data:
            v = data[QString('Length')]
            if v != self.length:
                self.length = v
                pos_str = ( '%d:%02d' % (v / 60, v % 60))
                self.positionLabel.setText("<b>/ "+pos_str+"</b>")

    def createMeter(self):
        pass

    def createPositionLabel(self):
        self.positionLabel = Label()
        self.positionLabel.setContentsMargins(0,0,0,0)
        self.positionLabel.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum, True))
        self.positionLabel.setAlignment(Qt.AlignRight)

    def createPlayControlsBar(self):
        self.controlsbar = Plasma.IconWidget()
        self.controlsbar_layout = QGraphicsLinearLayout(Qt.Horizontal)
        self.controlsbar_layout.setContentsMargins(0,0,0,0)
        self.controlsbar.setLayout(self.controlsbar_layout)
        self.controlsbar.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum))
        
    def createMiddle(self):
        self.middle = Plasma.IconWidget()
        self.middle_layout = QGraphicsLinearLayout(Qt.Vertical)
        self.middle_layout.setContentsMargins(0,0,0,0)
        self.middle.setLayout(self.middle_layout)
        self.middle.setIcon(KIcon(self.getPauseIcon()))
        #self.middle.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))

    def createMute(self):
        pass

    def createNext(self):
        self.next = MuteButton(self)
        self.next.setAbsSize(20)
        self.next.setSvg(self.svg_path , "next-normal")
        self.connect(self.next, SIGNAL("clicked()"), self.on_next_cb  )

    def createPrev(self):
        self.prev = MuteButton(self)
        self.prev.setAbsSize(20)
        self.prev.setSvg(self.svg_path, "prev-normal")        
        self.connect(self.prev, SIGNAL("clicked()"), self.on_prev_cb  )

    def createPlayPause(self):
        self.play = MuteButton(self)
        self.play.setAbsSize(20)
        self.play.setSvg(self.svg_path, "stop-normal")        
        self.connect(self.play, SIGNAL("clicked()"), self.on_play_cb  )

    def on_mute_cb(self):
        pass
    
    def on_next_cb(self):
        if self.useDbusWorkaround():
            self.veromix.pa.nowplaying_next(self.controller.destination())
        else:
            self.controller.startOperationCall(self.controller.operationDescription('next'))

    def on_prev_cb(self):
        if self.useDbusWorkaround():
            self.veromix.pa.nowplaying_prev(self.controller.destination())
        else:
            self.controller.startOperationCall(self.controller.operationDescription('previous'))
        
    def on_play_cb(self):
        if self.state == NowPlaying.Playing:
            if self.useDbusWorkaround():
                self.veromix.pa.nowplaying_pause(self.controller.destination())
            else:
                self.controller.startOperationCall(self.controller.operationDescription('pause'))
        else:
            if self.useDbusWorkaround():            
                self.veromix.pa.nowplaying_play(self.controller.destination())
            else:
                self.controller.startOperationCall(self.controller.operationDescription('play'))
        
    def on_slider_cb(self, value):
        pass

    def useDbusWorkaround(self):
        for name in self.getMpris2Clients():
            if str(self.controller.destination()) .find(name) == 0:
                return True
        False
    
    def getMpris2Clients(self):
        return self.veromix.applet.getMpris2Clients()
        
    def getDbusInfo(self):
        data = {}        
        status = self.veromix.pa.nowplaying_getPlaybackStatus(self.controller.destination())        
        data[QString('State')] =  u'paused'
        if status == 'Playing':
            data[QString('State')] =  u'playing'            
        metadata = self.veromix.pa.nowplaying_getMetadata(self.controller.destination())       
        if dbus.String("mpris:artUrl") in metadata.keys():
            val = str(metadata[dbus.String("mpris:artUrl")])[7:]
            if val != self.cover_string:                
                data[QString('Artwork')] =  QPixmap(val)
                self.cover_string = val
        if dbus.String("mpris:length") in metadata.keys():
            v =  int(metadata[str(dbus.String("mpris:length"))])  / 1000000 
            data[QString('Length')] = v
        data[QString('Position')] = int(self.veromix.pa.nowplaying_getPosition(self.controller.destination()))  / 1000000 
        return data
        
    def get_application_name(self):
        name = self.controller.destination()
        if name.indexOf("org.mpris.MediaPlayer2.")  == 0:
            return name[23:]
        if name.indexOf("org.mpris.")  == 0:
            return name[10:]
        return name
        
    def updateSortOrderIndex(self):
        sink = self.findSink()      
        if sink != None:
            new =  sink.sortOrderIndex - 1
            if self.sortOrderIndex != new:
                self.sortOrderIndex = new
                self.veromix.check_ItemOrdering()
        else:
            self.sortOrderIndex
    
    def matches(self, sink):
        sink = self.findSink()
        if sink == None:
            return False
        return True  
  
    def findSink(self):
        name = str(self.get_application_name()).lower()
        for sink in self.veromix.getSinkInputs():            
            if str(sink.text).lower() == name:
                return sink
        for sink in self.veromix.getSinkInputs():
            if str(sink.text).lower().find(name) >= 0 :
                return sink                      
        for sink in self.veromix.getSinkInputs():
            if str(sink.text).find(sink.text.lower()) >= 0 :
                return sink    
        return None

    def isNowplaying(self):
        return True    
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
from LabelSlider import LabelSlider
from Channel import Channel
from MuteButton  import *

class NowPlaying( Channel ):
    Stopped, Playing, Paused, NA = range(4)  
    
    def __init__(self,veromix, controller):
        self.controller = controller
        Channel.__init__(self, veromix)  
        self.index = -1
        self.state = NowPlaying.NA
        self.artist = ""
        self.title = ""
        self.album =""
        self.volume = 0
        self.position = 0
        self.length = 0
        

    def initArrangement(self):
        
        #self.setContentsMargins(6,3,6,0)
        #self.layout.setContentsMargins(6,3,6,10)
        self.svg_path = self.veromix.applet.package().filePath('images', 'buttons.svgz')
        self.createMiddle()      
        self.createPlayControlsBar()
        self.createPanel()
        self.createPanel()
        self.createPrev()
        self.createPlayPause()
        self.createNext() 

    def composeArrangement(self):
        self.layout.addItem(self.panel)
        
        #self.panel_layout.addStretch()
        self.controlsbar_layout.addItem(self.prev)
        self.controlsbar_layout.addStretch()
        self.controlsbar_layout.addItem(self.play)
        self.controlsbar_layout.addStretch()
        self.controlsbar_layout.addItem(self.next)
        
        self.middle_layout.addStretch()        
        self.middle_layout.addItem(self.controlsbar)
        
        self.panel_layout.addStretch()
        self.panel_layout.addItem(self.middle)
        self.panel_layout.addStretch()
        #self.panel_layout.addItem(self.meter)
        #self.panel_layout.addItem(self.mute)
        #self.panel_layout.addItem(self.mute)       


    def update_with_info(self, data):        
        self.updateState(data)
        self.updatePosition(data)
        self.updateArtistInfo(data)
        self.updateCover(data)
        
        
    def updateState(self,data):
        state = self.state
        if QString('State') in data:
            if data[QString('State')] == u'playing':
                state = NowPlaying.Playing
            elif data[QString('State')] == u'paused':
                state = NowPlaying.Paused
            elif data[QString('State')] == u'stopped':
                state = NowPlaying.Stopped

        if self.state != state:
            self.state = state
            if self.state == NowPlaying.Playing:
                self.play.setSvg(self.svg_path, "stop-normal")     
            else:
                self.play.setSvg(self.svg_path, "play-normal")     
                
        #self.checkPlayPause()
        #self.checkVisibility()
        #changed = True
        
        
    def updateCover(self,data):
        #self.mute.dataUpdated("amarok",data)
        if QString('Artwork') in data:
                self.middle.setIcon(QIcon(QPixmap(data[QString('Artwork')])))
        else:
            img = None
            #self.mute.setImage(QPixmap(data[QString('Artwork')]))
        pass
    
    def updateArtistInfo(self,data):
        if QString('Artist') in data:
            artist = data[QString('Artist')]
        #elif self.player != '':
            #artist = U(self.player)
            #artist = artist[artist.rfind('.') + 1:].title()
        else:
            artist = i18n('No Player')
          
        artist = self.controller.destination() +" " +artist
        #artist = self.
        if artist != self.artist:
            self.artist = artist
            if self.slider != None:
                self.slider.setBoldText(self.artist)
            changed = True

    def updatePosition(self, data):

        if QString('Position') in data:
            v = data[QString('Position')]
            if v != self.position:
                self.position = v
                if self.slider != None:
                    self.slider.setValue(v)
                    #self.current.setText('%d:%02d' % (v / 60, v % 60))            
            
        if QString('Length') in data:
            v = data[QString('Length')]
            if v != self.length:
                self.length = v
                if self.slider != None:
                    self.slider.setMaximum(v)
                    #self.total.setText('%d:%02d' % (v / 60, v % 60))

    def gugus(self):
        changed = False
        state = NowPlaying.Stopped
        
        if QString('Title') in data:
            title = U(data[QString('Title')])
            if self.state == NowPlaying.Paused:
                title += U(i18n(' (paused)'))
            if self.state == NowPlaying.Stopped:
                title += U(i18n(' (stopped)'))
        else:
            if self.state == NowPlaying.Stopped:
                title = U(i18n('Stopped'))
            else:
                title = U(i18n('N/A'))
        if title != self.title:
            self.title = title
            if self.slider != None:
                self.slider.setText(self.title)
            changed = True

        #if QString('Album') in data:
            #album = U(data[QString('Album')])
        #else:
            #album = ''
        #if self.album != album:
            #self.album = album
            #changed = True

        if QString('Artwork') in data:
            if changed:
                self.cover.setIcon(KIcon(QPixmap(data[QString('Artwork')])))
        else:
            img = None
            #self.meter.setImage(QPixmap(data[QString('Artwork')]))
            #if album != '':
                #key = artist + '|' + album
                #if key in self.coverCache:
                    #img = self.coverCache[key]
                #elif self.coverPlugin != None:
                    #img = self.coverPlugin(artist, album)
                    #self.coverCache[key] = img
            #if not img:
                #img = self.logo

            #if self.cover.image() != img:
                #self.cover.setImage(img)

        #if changed and self.formFactor() in [Plasma.Horizontal, Plasma.Vertical]:
            #self.artwork = self.cover.scaledPixmap(50, 50)
            #toolTip = Plasma.ToolTipContent(self.artist, self.title, self.artwork)
            #Plasma.ToolTipManager.self().setContent(self.applet, toolTip)

        #if QString('Volume') in data:
            #v = I(F(data[QString('Volume')]) * 100.0)
            #if v != self.volume:
                #self.volume = v
                #if self.slider != None:
                    #self.slider.setValue(v)
    def createMeter(self):
        pass
        #self.meter.setMeterType(Plasma.Meter.AnalogMeter)
        #self.meter.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum, True))
        #self.connect(self.meter, SIGNAL("clicked()"), self.on_show_info_widget  )

    def createPlayControlsBar(self):
        self.controlsbar = Plasma.IconWidget()
        self.controlsbar_layout = QGraphicsLinearLayout(Qt.Horizontal)
        self.controlsbar_layout.setContentsMargins(0,0,0,0)

        self.controlsbar.setLayout(self.controlsbar_layout)
        #self.controlsbar.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.controlsbar.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding))
        

        #self.setMaximumSize(QSizeF(self.BIGSIZE,self.BIGSIZE))
        
    def createMiddle(self):
        self.middle = Plasma.IconWidget()
        self.middle_layout = QGraphicsLinearLayout(Qt.Vertical)
        #self.middle_layout.setContentsMargins(6,8,6,0)


        self.CONTROLSBAR_SIZE = 128
        self.middle.setPreferredSize(QSizeF(self.CONTROLSBAR_SIZE,self.CONTROLSBAR_SIZE))
        self.middle.setMaximumSize(QSizeF(self.CONTROLSBAR_SIZE,self.CONTROLSBAR_SIZE))

        self.middle.setLayout(self.middle_layout)
        #self.middle.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))

        self.createSlider()
        self.connect(self.slider, SIGNAL("valueChanged(int)"), self.on_slider_cb  )
        #self.middle_layout.addItem(self.slider)

    def createMute(self):
        pass

    def createNext(self):
        self.next = MuteButton(self)
        self.next.setSvg(self.svg_path , "next-normal")
        self.connect(self.next, SIGNAL("clicked()"), self.on_next_cb  )

    def createPrev(self):
        self.prev = MuteButton(self)
        self.prev.setSvg(self.svg_path, "prev-normal")        
        #self.prev.setPrefix('prev')
        self.connect(self.prev, SIGNAL("clicked()"), self.on_prev_cb  )

    def createPlayPause(self):
        #self.mute = NowRocking(self.veromix)
        self.play = MuteButton(self)
        self.play.setSvg(self.svg_path, "stop-normal")        
        self.connect(self.play, SIGNAL("clicked()"), self.on_play_cb  )

    def on_mute_cb(self):
        pass
    
    def on_next_cb(self):
        #self.veromix.pa.nextTrack()
        self.controller.startOperationCall(self.controller.operationDescription('next'))

    def on_prev_cb(self):
        self.controller.startOperationCall(self.controller.operationDescription('previous'))
        
    def on_play_cb(self):
        if self.state == NowPlaying.Playing:
            self.controller.startOperationCall(self.controller.operationDescription('pause'))
        else:
            self.controller.startOperationCall(self.controller.operationDescription('play'))
        
    def on_slider_cb(self, value):
        pass


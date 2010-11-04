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
#from nowrocking.image import *
#from nowrocking.helpers import *
#from nowrocking.NowRocking import *

class NowPlaying( Channel ):
    Stopped, Playing, Paused, NA = range(4)  
    
    def __init__(self,veromix, controller):
        self.controller = controller
        print "CONTROLLER nowplaying", self.controller
        Channel.__init__(self, veromix)  
        print "------------------------------"
        self.index = -1
        self.state = NowPlaying.NA
        self.artist = ""
        self.title = ""
        self.album =""
        self.volume = 0
        self.position = 0
        self.length = 0
        

    def initArrangement(self):
        #self.createExtender()
        self.createPanel()
        #self.meter = Image()        
        print "CONTROLLER nowplaying2", self.controller
        #self.mute = NowRocking(self.veromix, self.controller)
        #self.BIGSIZE = 56
        #self.meter.setPreferredSize(QSizeF(self.BIGSIZE,self.BIGSIZE))
        #self.meter.setMaximumSize(QSizeF(self.BIGSIZE,self.BIGSIZE))
        #self.meter.setMinimumSize(QSizeF(self.BIGSIZE,self.BIGSIZE))
        self.createMute()
        #self.createMiddle()
        #self.createMeter()
        

    def composeArrangement(self):
        self.layout.addItem(self.panel)
        
        #self.panel.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        #self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        #self.mute.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        
        self.panel_layout.addStretch()
        self.panel_layout.addItem(self.mute)
        self.panel_layout.addStretch()
        #self.panel_layout.addItem(self.meter)
        #self.panel_layout.addItem(self.mute)
        #self.panel_layout.addItem(self.mute)        


    #def composeArrangement(self):
        #self.layout.addItem(self.mute)
        #self.panel_layout.addItem(self.mute)  
        #self.panel_layout.addItem(self.meter)
        #self.panel_layout.addItem(self.middle)      


    def update_with_info(self, data):
        #self.mute.dataUpdated("amarok",data)
        pass
    
    def gugus(self):
        changed = False
        state = NowPlaying.Stopped
        #if QString('State') in data:
            #if U(data[QString('State')]) == u'playing':
                #state = NowPlaying.Playing
            #elif U(data[QString('State')]) == u'paused':
                #state = NowPlaying.Paused

        #if self.state != state:
            #self.state = state
            #self.checkPlayPause()
            #self.checkVisibility()
            #changed = True

        if QString('Artist') in data:
            artist = U(data[QString('Artist')])
        #elif self.player != '':
            #artist = U(self.player)
            #artist = artist[artist.rfind('.') + 1:].title()
        else:
            artist = U(i18n('No Player'))
        if artist != self.artist:
            self.artist = artist
            if self.slider != None:
                self.slider.setBoldText(self.artist)
            changed = True

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
                self.cover.setImage(QPixmap(data[QString('Artwork')]))
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

        if QString('Position') in data:
            v = I(data[QString('Position')])
            if v != self.position:
                self.position = v
                if self.slider != None:
                    self.slider.setValue(v)
                    #self.current.setText('%d:%02d' % (v / 60, v % 60))

        if QString('Length') in data:
            v = I(data[QString('Length')])
            if v != self.length:
                self.length = v
                if self.slider != None:
                    self.slider.setMaximum(v)
                    #self.total.setText('%d:%02d' % (v / 60, v % 60))

    def createMeter(self):
        pass
        #self.meter.setMeterType(Plasma.Meter.AnalogMeter)
        #self.meter.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum, True))
        #self.connect(self.meter, SIGNAL("clicked()"), self.on_show_info_widget  )

    def createMute(self):
        #self.mute = NowRocking(self.veromix)
        self.mute = MuteButton(self.veromix)
        #self.BIGSIZE = 56
        #self.mute.setPreferredSize(QSizeF(self.BIGSIZE,self.BIGSIZE))
        #self.mute.setMaximumSize(QSizeF(self.BIGSIZE,self.BIGSIZE))
        #self.mute.setMinimumSize(QSizeF(self.BIGSIZE,self.BIGSIZE))
        #self.mute.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum,True) )
        #self.connect(self.mute, SIGNAL("clicked()"), self.on_mute_cb  )

    def on_slider_cb(self, value):
        pass
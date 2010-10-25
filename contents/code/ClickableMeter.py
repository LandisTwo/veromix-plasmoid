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

class ClickableMeter(Plasma.Meter):
    
    def __init__(self):
        Plasma.Meter.__init__(self)
        #self.acceptedMouseButtons()
        #self.acceptHoverEvents()
        #self.setAcceptedMouseButtons(Qt.LeftButton)
        
    def mousePressEvent (self, event):
        self.emit(SIGNAL("clicked()"))
 
    #def hoverEnterEvent (self, e):
        #print "move.."
    
    #def shape(self):
        #rect = self.boundingRect()
        #path = QPainterPath()
        ##pridnt rect
        #path.addRect(rect)
        #return path
        
    #def boundingRect(self):
        #return QRectF(0,0, 32,32)
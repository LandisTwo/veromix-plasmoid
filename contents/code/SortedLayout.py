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
from PyKDE4.plasma import Plasma
from PyKDE4 import plasmascript
from PyKDE4.kdeui import *
from PyKDE4.kdecore import *
from PyKDE4.kdecore import *
from PyKDE4.plasma import * 
import sys

class SortedLayout(QGraphicsLinearLayout):

    def __init__(self, orient, reverse):
        QGraphicsLinearLayout.__init__(self, orient)
        self.reverse= reverse

    def check_ItemOrdering(self, sinks):
        while(self.needs_ordering(sinks)):
            self.order_items(sinks)  

    def order_items(self, sinks):
       sorting = self.sort(sinks.values(), 'sortOrderIndex')
       for i in range(0,len(sorting)):
            if self.itemAt(i).graphicsItem ()  != sorting[i]:      
                item = self.itemAt(i).graphicsItem()
                index = sorting.index(item)
                self.insertItem(index , item )
                return
                
    def needs_ordering(self, sinks):
        sorting = self.sort(sinks.values(), 'sortOrderIndex')
        for i in range(0,len(sorting)):
            if self.itemAt(i).graphicsItem ()  != sorting[i]:      
                return True
        return False       
        
    def sort(self, objects,sortAttrib):
        nlist = map(lambda object, sortAttrib=sortAttrib: (getattr(object, sortAttrib),object), objects)
        nlist.sort(reverse=self.reverse)
        return map(lambda (key, object): object, nlist)        
        
        
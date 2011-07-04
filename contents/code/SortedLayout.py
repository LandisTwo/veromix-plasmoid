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

from PyQt4.QtGui import *
from SinkInputUI import InputSinkUI
from SinkInputUI import SinkUI
from SinkMbeqUI import SinkMbeqUI

class SortedLayout(QGraphicsLinearLayout):

    def __init__(self, orient, reverse):
        QGraphicsLinearLayout.__init__(self, orient)
        self.reverse= reverse
        self.channels = {}
        self.sink_pool = []
        self.sink_input_pool = []

    def get_new_sink_input(self, veromix):
        if len(self.sink_input_pool) == 0:
            return InputSinkUI(veromix)
        else:
            val = self.sink_input_pool[0]
            self.sink_input_pool.remove(val)
            val.show()
            return val

    def get_new_sink(self, veromix, sink):
        sink_type = None
        if "device.ladspa.module" in sink.properties().keys(): # and
            sink_type = sink.properties()["device.ladspa.module"]         #"device.ladspa.module"
            print sink_type
            return self._get_new_ladspa_sink(veromix, str(sink_type))
        else:
            return self._get_new_sink(veromix)

    def _get_new_ladspa_sink(self, veromix, sink_type):
        pool =  []
        for sink in self.sink_pool:
            if sink.get_ladspa_type() == sink_type:
                pool.append(sink)
        if len(pool) == 0:
            return SinkMbeqUI(veromix)
        else:
            val = pool[0]
            self.sink_pool.remove(val)
            val.show()
            return val

    def _get_new_sink(self, veromix):
        if len(self.sink_pool) == 0:
            return SinkUI(veromix)
        else:
            val = self.sink_pool[0]
            self.sink_pool.remove(val)
            val.show()
            return val

    def getChannels(self):
        return self.channels

    def get_sinkoutput_widgets(self):
        toreturn = []
        for index in self.channels.keys() :
            if self.channels[index].isSinkOutput():
                toreturn.append(self.channels[index])
        return toreturn

    def get_sink_widgets(self):
        toreturn = []
        for index in self.channels.keys() :
            if self.channels[index].isSink():
                toreturn.append(self.channels[index])
        return toreturn

    def get_sinkinput_widgets(self):
        toreturn = []
        for index in self.channels.keys() :
            if self.channels[index].isSinkInput():
                toreturn.append(self.channels[index])
        return toreturn

    def get_mediaplayer_widgets(self):
        toreturn = []
        for index in self.channels.keys() :
            if self.channels[index].isNowplaying():
                toreturn.append(self.channels[index])
        return toreturn

    def getChannel(self, key):
        if key in self.channels.keys():
            return self.channels[key]
        return None

    def addChannel(self, key, widget):
        #for i in range(0,len(self.channels.keys())):
            #print "a",i, self.itemAt(i).graphicsItem().name  ," so" , self.itemAt(i).graphicsItem().sortOrderIndex
        if(key not in self.channels.keys()):
            self.channels[key]  = widget
            for i in self.get_mediaplayer_widgets():
                i.updateSortOrderIndex()
            sorting = self.sort(self.channels.values(), 'sortOrderIndex')
            index = sorting.index(widget)
            self.insertItem(index, widget )
            #print "inserting at",  index, key, widget.sortOrderIndex

    def removeChannel(self, key):
        if(key  in self.channels.keys()):
            self.channels[key].hide()
            self.removeItem(self.channels[key])
            if self.channels[key].isSinkInput():
                self.sink_input_pool.append(self.channels[key])
            if self.channels[key].isSink():
                self.sink_pool.append(self.channels[key])
            #self.channels[key].deleteLater()
            del self.channels[key]

    def check_ItemOrdering(self):
        while(self.needs_ordering()):
            self.order_items()

    def order_items(self):
        sorting = self.sort(self.channels.values(), 'sortOrderIndex')
        #for i in range(0,len(sorting)):
            #print "m",i, self.itemAt(i).graphicsItem().name  ," so" , self.itemAt(i).graphicsItem().sortOrderIndex
        for i in range(0,len(sorting)):
            if self.itemAt(i).graphicsItem ()  != sorting[i]:
                item = self.itemAt(i).graphicsItem()
                index = sorting.index(item)
                self.insertItem(index , item )
                #print "order item from",  i, "to", index, item.name,item.sortOrderIndex
                return

    def needs_ordering(self):
        for c in self.channels.values():
            c.updateSortOrderIndex()
        sorting = self.sort(self.channels.values(), 'sortOrderIndex')
        for i in range(0,len(sorting)):
            if self.itemAt(i).graphicsItem ()  != sorting[i]:
                return True
        return False

    def sort(self, objects,sortAttrib):
        nlist = map(lambda object, sortAttrib=sortAttrib: (getattr(object, sortAttrib),object), objects)
        nlist.sort(reverse=self.reverse)
        return map(lambda (key, object): object, nlist)

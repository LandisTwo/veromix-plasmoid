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

import datetime, dbus
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyKDE4.plasma import Plasma
from PyKDE4.kdeui import KIcon
from PyKDE4.kdecore import *

from PulseAudioProxy import PulseAudio
from SortedLayout import SortedLayout
from LockableScrollWidget import LockableScrollWidget
from SinkUI import SinkUI
from SinkInputUI import InputSinkUI
from SourceUI import SourceUI
from SourceOutputUI import SourceOutputUI
from NowPlaying import NowPlaying

class VeroMix(QGraphicsWidget):
    sinkOutputChanged = pyqtSignal()

    def __init__(self,parent):
        QGraphicsWidget.__init__(self)
        self.applet = parent
        self.pa = None            
        self.last_resize_running = datetime.datetime.now()
        self.last_resize_running_timer_running = False
        self.card_infos = {}

    def init(self):
        self.setAcceptsHoverEvents (True)
        self.layout = QGraphicsLinearLayout(Qt.Vertical, self)
        self.layout.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum))

        self.scroller = LockableScrollWidget(self)
        self.scroller.setMinimumSize(120,90)
        self.layout.addItem(self.scroller)
        if self.applet.formFactor() != Plasma.Planar  :
            self.scroller.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.source_panel = QGraphicsWidget()
        self.sink_panel = QGraphicsWidget()

        self.scrolled_panel_layout = QGraphicsLinearLayout(Qt.Vertical)
        self.scrolled_panel_widget = QGraphicsWidget()
        self.scrolled_panel_widget.setLayout(self.scrolled_panel_layout)
        self.scrolled_panel_layout.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        self.scrolled_panel_layout.setContentsMargins(0,0,0,6)

        self.showsTabs =  not self.applet.useTabs()
        self.switchView(True)

        self.source_panel_layout = SortedLayout(Qt.Vertical, False)
        self.source_panel.setLayout(self.source_panel_layout)
        self.source_panel_layout.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        if self.showsTabs:
            self.source_panel_layout.addStretch()

        self.sink_panel_layout = SortedLayout(Qt.Vertical, True)
        self.sink_panel_layout.setSpacing(0)

        self.sink_panel.setLayout(self.sink_panel_layout)
        self.sink_panel_layout.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))

        self.layout.setContentsMargins(0,0,0,0)
        self.source_panel_layout.setContentsMargins(0,0,0,12)
        self.sink_panel_layout.setContentsMargins(0,0,0,0)

        #QTimer.singleShot(4000, self.start_pa)
        self.start_pa()
        self.start_nowplaying()

    def switchView(self, startup=False):
        if self.showsTabs:
            self.scrolled_panel_layout = QGraphicsLinearLayout(Qt.Vertical)
            scrolled_panel = QGraphicsWidget()
            scrolled_panel.setLayout(self.scrolled_panel_layout)
            self.scrolled_panel_layout.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
            self.scrolled_panel_layout.setContentsMargins(0,0,0,6)
            self.scrolled_panel_layout.addItem(self.source_panel)
            self.scrolled_panel_layout.addItem(self.sink_panel)
        else:
            scrolled_panel = Plasma.TabBar()
            scrolled_panel.addTab(i18n("Playback"), self.sink_panel)
            scrolled_panel.addTab(i18n("Record"), self.source_panel)
            self.source_panel.show()

        self.scrolled_panel = scrolled_panel
        self.showsTabs = not self.showsTabs
        self.scroller.setWidget(self.scrolled_panel)
        if not startup:
            self.check_geometries()

    def on_update_configuration(self):
        for source in self.source_panel_layout.getChannels().values():
            source.on_update_configuration()
        for sink in self.sink_panel_layout.getChannels().values():
            sink.on_update_configuration()

    # connect to pulseaudio(dbus) callbacks
    def start_pa(self):
        try:
            self.pa = PulseAudio(self)
        except Exception, e:
            self.showMessage(KIcon("script-error"), i18n("There is a problem with the backgroud-service. \
                                                        <ul> \
                                                        <li>If you just upgraded try killing the process named: VeromixServiceMain.py and relaunch this plasmoid</li> \
                                                        <li>If you don't know how to do that consider rebooting</li></ul><br/>\
                                                        <a href=\"http://code.google.com/p/veromix-plasmoid/wiki/VeromixComponents#The_service:_VeromixServiceMain.py\">See wiki for more details</a> <span style=\"font-size: small;\">(right click and copy url)</span>."))
            print "\nError connecting to veromix-service:\n" , e, "\n"
            return
        self.connect(self.pa, SIGNAL("on_sink_input_info(PyQt_PyObject)"), self.on_sink_input_info)
        self.connect(self.pa, SIGNAL("on_sink_info(PyQt_PyObject)"), self.on_sink_info)
        self.connect(self.pa, SIGNAL("on_source_output_info(PyQt_PyObject)"), self.on_source_output_info)
        self.connect(self.pa, SIGNAL("on_source_info(PyQt_PyObject)"), self.on_source_info)

        self.connect(self.pa, SIGNAL("on_sink_remove(int)"), self.on_remove_sink)
        self.connect(self.pa, SIGNAL("on_sink_input_remove(int)"), self.on_remove_sink_input)
        self.connect(self.pa, SIGNAL("on_source_remove(int)"), self.on_remove_source)
        self.connect(self.pa, SIGNAL("on_source_output_remove(int)"), self.on_remove_source_output)
        
        self.connect(self.pa, SIGNAL("on_volume_meter_sink(int, float )"), self.on_volume_meter_sink)
        self.connect(self.pa, SIGNAL("on_volume_meter_sink_input(int, float )"), self.on_volume_meter_sink_input)
        self.connect(self.pa, SIGNAL("on_volume_meter_source(int, float )"), self.on_volume_meter_source)

        self.connect(self.pa, SIGNAL("on_card_info(PyQt_PyObject)"), self.on_card_info)
        self.connect(self.pa, SIGNAL("on_card_remove(int)"), self.on_remove_card)
        self.pa.requestInfo()

    def start_nowplaying(self):
        self.applet.nowplaying_player_added.connect(self.on_nowplaying_added)
        self.applet.nowplaying_player_removed.connect(self.on_nowplaying_removed)
        self.applet.nowplaying_player_dataUpdated.connect(self.on_nowplaying_dataUpdated)

## helpers UI

    def check_geometries(self):
        self.check_ItemOrdering()
        count = 0
        for source in self.source_panel_layout.getChannels().values():
            if source.isSourceOutput():
                count += 1
        self.setSourcesPanelVisible( count > 0 )
        # REstore
        #self.sink_panel.adjustSize()
        #self.source_panel.adjustSize()
        #self.scrolled_panel.adjustSize()
        if self.applet.formFactor()  == Plasma.Planar:
            pass
        else:
            self.trigger_schedule_timer()
        #self.updateGeometry()

    def do_scheduled_resize(self):
        now = datetime.datetime.now()
        if  (now - self.last_resize_running).seconds > 1:
            self.adjustSize()
            self.setMinimumHeight(self.scrolled_panel.preferredSize().height())
            self.setMaximumHeight(self.scrolled_panel.preferredSize().height())
            self.last_resize_running = datetime.datetime.now()
        else:
            self.trigger_schedule_timer()

    def trigger_schedule_timer(self):
        if self.last_resize_running_timer_running:
                return
        self.last_resize_running_timer_running = True
        QTimer.singleShot(1000, self.on_schedule_resize_timer_cb)

    def on_schedule_resize_timer_cb(self):
        self.last_resize_running_timer_running = False
        self.do_scheduled_resize()

    def check_ItemOrdering(self):
        self.source_panel_layout.check_ItemOrdering()
        self.sink_panel_layout.check_ItemOrdering()
        pass

    def setSourcesPanelVisible(self, aBoolean):
        if self.showsTabs:
            return
        #if self.applet.isPopupShowing():
        if aBoolean :
            self.source_panel.show()
            self.scrolled_panel_layout.insertItem(0, self.source_panel)
        else:
            self.source_panel.hide()
            self.scrolled_panel_layout.removeItem(self.source_panel)

 ## callbacks source output

    def on_source_output_info(self,  sink):
        key = "sourceoutput" + str(sink.index)
        if not self.update_channel(key ,sink, self.source_panel_layout ):
            widget =  SourceOutputUI(  self)
           # FIXME sliders want to be visible when added, else we get a crash
            self.setSourcesPanelVisible(True)
            self.add_channel(key, widget , sink, self.source_panel_layout )

    def on_remove_source_output(self, index):
        # FIXME sliders want to be visible when added, else we get a crash
        self.setSourcesPanelVisible(True)
        self.remove_channel("sourceoutput" + str(index), self.source_panel_layout )

 ## callbacks source

    def on_source_info(self,  sink):
        key = "source" + str(sink.index)
        if not self.update_channel(key ,sink, self.source_panel_layout ):
            widget =  SourceUI(  self)
           # FIXME sliders want to be visible when added, else we get a crash
            self.setSourcesPanelVisible(True)
            self.add_channel(key, widget , sink, self.source_panel_layout )

    def on_remove_source(self, index):
        # FIXME sliders want to be visible when added, else we get a crash
        self.setSourcesPanelVisible(True)
        self.remove_channel("source" + str(index), self.source_panel_layout )

 ## callbacks sink

    def on_sink_info(self,sink):
        key = "sink" + str(sink.index)
        if not self.update_channel(key ,sink, self.sink_panel_layout ):
            widget =  SinkUI(  self)
            self.add_channel(key, widget , sink, self.sink_panel_layout )
            widget.muteInfo.connect(self.updateIcon)
            self.sinkOutputChanged.emit()
        sink.printDebug()

    def on_remove_sink(self, index):
        self.remove_channel("sink" + str(index), self.sink_panel_layout )
        self.sinkOutputChanged.emit()

 ## callbacks sink input

    def on_sink_input_info(self,  sink):
        key = "sinkinput" + str(sink.index)
        if not self.update_channel(key ,sink, self.sink_panel_layout ):
            self.add_channel(key, self.sink_panel_layout.getNewInputSink(self), sink , self.sink_panel_layout)

    def on_remove_sink_input(self, index):
        self.remove_channel("sinkinput" + str(index), self.sink_panel_layout)

 ## callbacks card info
    def on_card_info(self, info):
        self.card_infos[info.name] = info
        info.printDebug()

    def on_remove_card(self, index):
        for key in self.card_infos.keys():
            card = self.card_infos[key]
            if int(card.index) == int(index):
                del self.card_infos[key]

## Callbacks volume menters

    def on_volume_meter_sink(self, index, level):
        for sink in self.sink_panel_layout.getChannels().values():
            sink.on_update_meter(index,int(level), len(self.sink_panel_layout.getChannels()))
            
    def on_volume_meter_sink_input(self, index, level):
        for sink in self.sink_panel_layout.getChannels().values():
            sink.on_update_meter(index,int(level), len(self.sink_panel_layout.getChannels()))

    def on_volume_meter_source(self, index, level):
        sources = self.source_panel_layout.getChannels().values()
        for source in sources:
            source.on_update_meter(index,int(level), len(sources))

    def resizeEvent(self, e):
        self.emit(SIGNAL("resized()"))

### panel-icon callbacks

    def on_toggle_mute(self):
        sink = self.getDefaultSink()
        if sink != None:
            sink.on_mute_cb()
        self.applet.showTooltip()

    def on_step_volume_up(self):
        self.on_step_volume(True)

    def on_step_volume_down(self):
        self.on_step_volume(False)

    def on_step_volume(self, up):
        sink = self.getDefaultSink()
        if sink != None:
            sink.on_step_volume(up)
        self.applet.showTooltip()

### callback nowplaying

    def on_nowplaying_added(self, name, controller):
        #self.sink_panel_layout.setSpacing(0)
        self.add_channel(name, NowPlaying(self, controller),None, self.sink_panel_layout)

    def on_nowplaying_removed(self, name):
        self.remove_channel(name,self.sink_panel_layout)

    def on_nowplaying_dataUpdated(self, name, values):
        channel = self.sink_panel_layout.getChannel(name)
        if channel:
            channel.update_with_info(values)

    #def on_mpris2_properties_changed(self, destination, properties):
        #print "d", destination, type(destination)
        #for i in properties.keys():
            #print i
            #print "---"
            #print properties[i]
            #print "--------"

        #print "==="
        #self.on_nowplaying_dataUpdated(destination, properties)
        #channel = self.sink_panel_layout.getChannel(str(destination))
        #if channel:
            #print "got channel"
            #channel.convert_dbus_info(values)

### panel icons

    def updateIcon(self, muted):
        self.applet.updateIcon()

### helpers accessing channels

    def add_channel(self, key, widget, sink, target_layout):
        if sink:
            widget.update_with_info(sink)
        target_layout.addChannel(key, widget)
        self.check_geometries()
        return widget

    def update_channel(self, key, sink, target_layout):
        if target_layout.getChannel(key) :
            target_layout.getChannel(key).update_with_info(sink)
            self.check_ItemOrdering()
            return True
        else:
            return False

    def remove_channel(self, key, target_layout):
        target_layout.removeChannel(key)
        self.check_geometries()

    def getSinkOutputs(self):
        return self.sink_panel_layout.getSinkOutputs()

    def getSinkInputs(self):
        return self.sink_panel_layout.getSinkInputs()

    def getNowPlaying(self):
        return self.sink_panel_layout.getNowPlaying()

    def getDefaultSink(self):
        for sink in self.sink_panel_layout.getChannels().values():
            if sink.isDefaultSink():
                return sink
## helpers

    def get_card_info_for(self, sink):
        card_identifier = dbus.String(u'alsa.long_card_name') #u'sysfs.path'        
        info = self._get_card_info_for(sink, card_identifier)
        if info:
            return info
        card_identifier = dbus.String(u'device.string')
        return self._get_card_info_for(sink, card_identifier)

    def _get_card_info_for(self, sink, card_identifier):
        if sink.pa_sink == None:
            print "get_card_info_for: no pa_sink"
            return None
        if card_identifier  not in sink.pa_sink.props.keys():
            print "get_card_info_for: key: ", card_identifier," not found in:",  sink.pa_sink.props.keys()
            return None
        for info in self.card_infos.values():
            if card_identifier  in info.properties.keys():
                if info.properties[dbus.String(card_identifier)] == sink.pa_sink.props[card_identifier]:
                    print "get_card_info_for found"
                    return info
        return None

    def get_meter_visible(self):
        return self.applet.get_meter_visible()

    def get_max_volume_value(self):
        return self.applet.get_max_volume_value()

    def get_auto_mute(self):
        return self.applet.get_auto_mute()

    def getPulseAudio(self):
        return self.pa

    def query_application(self, needle):
        return self.applet.query_application(needle)

    def showMessage(self, icon, message):
        self.applet.showMessage(icon, message, Plasma.ButtonOk)

    def doExit(self):
        for i in self.sink_panel_layout.getChannels().values():
            # if a slider is not visible, plasmoidviewer crashes if the slider is not removed before exit... (dont ask me)
            i.removeSlider()
        for i in self.source_panel_layout.getChannels().values():
            # if a slider is not visible, plasmoidviewer crashes if the slider is not removed before exit... (dont ask me)
            i.removeSlider()

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

class Label(Plasma.Label):
    def __init__(self):
        Plasma.Label.__init__(self)
        self.text = ""
        self.bold_text = ""
        
    def setText(self, text):
        if text:
            self.text = text
        Plasma.Label.setText(self, "<b>"+self.bold_text + "</b> " + self.text)
    
    def setBoldText(self,text):
        if text:    
            self.bold_text = text
        self.setText(self.text)
    

class LabelSlider(Plasma.Slider):

    def __init__(self):
        Plasma.Slider.__init__(self)
        self.text=""
        self.bold_text = ""
        self.draw_slider = True
        
    def setText(self, text):
        if text:
            self.text = text
    
    def setBoldText(self,text):
        if text:
            self.bold_text = text

    def hideSlider(self):
        self.draw_slider = False

    def paint(self, painter, option, widget_p):
        widget = self.nativeWidget()
        if self.widget and widget.width() > 0:
            size = 10
            font = QFont()
            font.setPixelSize(size)
            font.setBold(True)
            painter.setPen(Plasma.Theme.defaultTheme().color(Plasma.Theme.TextColor))
            
            # Check if the font is too big
            fm = QFontMetrics(font)
            font.setPointSize(size)
            message = self.bold_text + " " + self.text
            if fm.width(message) > widget.width():
                while fm.width(message) > widget.width() and size > 0 and len(message) > 0:
                    #size = size - 1
                    message = message[0:-1]
                    #font.setPointSize(size)
                    fm = QFontMetrics(font)
                    #print size
            painter.setFont(font)
            text_target =  QRect(widget.rect())
            text_target.moveTo(0 ,-5)
            fm = QFontMetrics(font)
            bold_text_width = fm.width(self.bold_text + " ")
            if len(message) > len(self.bold_text + " ") :
                painter.drawText(text_target, Qt.AlignTop | Qt.AlignLeft, self.bold_text + " ")
                cut = len(message) - len(self.bold_text + " ")
                if True:
                    msg = self.text[ 0:cut ]
                    font.setBold(False)
                    painter.setFont(font)
                    painter.setPen(Plasma.Theme.defaultTheme().color(Plasma.Theme.TextColor))
                    text_target.moveTo( bold_text_width ,-5)            
                    painter.drawText(text_target, Qt.AlignTop | Qt.AlignLeft, msg)
            else:
                painter.drawText(text_target, Qt.AlignTop | Qt.AlignLeft, message)
            if self.draw_slider:
                Plasma.Slider.paint(self, painter, option, widget)
            
            
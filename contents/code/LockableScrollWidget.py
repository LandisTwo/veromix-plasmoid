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

class LockableScrollWidget(Plasma.ScrollWidget):

    def __init__(self,parent):
        self.locked = True
        Plasma.ScrollWidget.__init__(self,parent)

    def sceneEventFilter(self, item, event):
        if self.locked:
            return False
        else:
            return Plasma.ScrollWidget.sceneEventFilter(self, item, event)

    def beLocked(self):
        self.locked = True

    def beUnLocked(self):
        self.locked = False

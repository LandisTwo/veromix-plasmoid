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

import sys, os,commands
from xdg import BaseDirectory
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyKDE4.plasma import Plasma
from PyKDE4.kdeui import KIcon

def updateMetadataDesktop(applet):
    applet.layout = QGraphicsLinearLayout(Qt.Vertical)
    applet.setLayout(applet.layout)
    icon = Plasma.IconWidget("Please remove and re-add myself")
    icon.setIcon(KIcon("dialog-information"))
    applet.layout.addItem(icon)
    commands.getstatusoutput("cp " + unicode(applet.package().path()) + "metadata.desktop.kde4.4 $(kde4-config  --localprefix )share/apps/plasma/plasmoids/veromix-plasmoid/metadata.desktop" )
    commands.getstatusoutput("cp " + unicode(applet.package().path()) + "metadata.desktop.kde4.4 $(kde4-config  --localprefix )share/kde4/services/plasma-applet-veromix-plasmoid.desktop" )
    commands.getstatusoutput("kbuildsycoca4" )
    applet.showMessage(KIcon("dialog-information"),'<b>Configuration updated</b><br/> \
            Because of a known bug in KDE 4.4 initialization of Veromix failed.<br/><br/>\
            A workaround is now installed.<br/><br/>\
            Please <b>remove</b> this applet and <b>add</b> Veromix again to your desktop/panel (alternatively you can restart plasma-desktop).<br/><br/> \
            Sorry for the inconvenience.<br/><br/>\
            <a href="http://code.google.com/p/veromix-plasmoid/wiki/VeromixComponents#KDE_4.4_compatibility">See wiki for more details</a> <span style="font-size: small;">(right click and copy url)</span>. ', Plasma.ButtonOk)

def createDbusServiceDescription(applet):
    print "Outputting dbus-servie file"
    service_dir = os.path.join(BaseDirectory.xdg_data_home,"dbus-1/services/")
    createDirectory(service_dir)
    # File to create
    fn = service_dir+"org.veromix.pulseaudio.service"

    exec_dir = unicode(applet.package().path()) + "dbus-service/VeromixServiceMain.py"

    # File contents
    c = []
    c.append("[D-BUS Service]\n")
    c.append("Name=org.veromix.pulseaudioservice\n")
    c.append("Exec="+exec_dir+"\n")

    # Write file
    try:
        f = open(fn,"w")
        f.writelines(c)
        f.close()
    except:
        print "Problem writing to file: "+fn
        print "Unexpected error:", sys.exc_info()[0]
    commands.getstatusoutput("chmod u+x "+exec_dir)

def createDirectory(d):
    if not os.path.isdir(d):
        try:
            os.makedirs(d)
        except:
            print "Problem creating directory: "+d
            print "Unexpected error:", sys.exc_info()[0]        
            
def pixmapFromSVG( name):
        svg = Plasma.Svg()
        svg.setImagePath("icons/audio")
        if not svg.isValid():
            return KIcon(name).pixmap(22,22)
        svg.setContainsMultipleImages(False)
        return svg.pixmap(name)            
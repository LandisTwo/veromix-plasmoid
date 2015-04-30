# Introduction #

Veromix has two components:
  * a **widget** (plasmoid) that you can place anywhere on your desktop.
  * a **service** (program) that collects data and sends notifications to the widgets.


## The service: `veromix-service-qt.py` (old name: VeromixServiceMain.py) ##

The service is launched automatically by dbus. For this to work veromix installs a service
description-file in ~/.local/share/dbus-1/services/ called org.veromix.pulseaudio.service.
If this file exists dbus starts the service (when the first widget is added to the desktop). Your should see a process called `VeromixServiceMain.py` in you process list. (in a console you can check with:
`ps -ef | grep veromix` )

## The Widget ##
The widget can be place multiple times on your desktop, but there should only be one service-process running.


# Troubleshooting #

## Service autostart ##
**Symptom:** Widget is empty.

The file ~/.local/share/dbus-1/services/org.veromix.pulseaudio.service should be created automatically after you first launch veromix. The contents of the file should look like this:
```
[D-BUS Service]
Name=org.veromix.pulseaudioservice
Exec=USERS_HOME_DIR.kde/share/apps/plasma/plasmoids/veromix-plasmoid/dbus-service/veromix-service-qt.py
```
_Note: USERS\_HOME\_DIR is a placeholder_

  1. If this file does not exist you can try adding it manually.
  1. If dbus is not automatically starting the service, you can add `veromix-service-qt.py` to the list of autostart items (KDE systemsettings -> Autostart).


## How to collect debugging information ##
First kill the process called `veromix-service-qt.py`, in a terminal you can execute:
```
ps -ef | grep  VeromixService  | grep -v grep | awk '{print $2}' | xargs kill -s TERM
```

Then start the service manually:
```
~/.kde/share/apps/plasma/plasmoids/veromix-plasmoid/dbus-service/veromix-service-qt.py
```
open a new terimnal window and execute:
```
cd ~/.kde/share/apps/plasma/plasmoids/veromix-plasmoid/
plasmoidviewer .
```

Please search and report bugs [here](http://code.google.com/p/veromix-plasmoid/issues/list)
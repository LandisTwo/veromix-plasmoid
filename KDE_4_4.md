There is a bug in KDE 4.4 that is fixed in 4.5. To be backward-compatible veromix checks your KDE version on startup and then installs the workaround.

There problem comes from the description-file of the plasmoid:  ~/.kde/share/apps/plasma/plasmoids/veromix-plasmoid/metadata.desktop

In KDE 4.4 metadata.desktop should define:
`ServiceTypes=Plasma/PopupApplet`

In KDE 4.5 and above:
`ServiceTypes=Plasma/Applet,Plasma/PopupApplet`

This change is automatically installed if veromix detects KDE 4.4, but it requires plasma to restart. You can to that by:
  * restart your computer
  * logoff and login again
  * restart plasma-desktop (hit: Alt-F2 and execute: "killall plasma-desktop; plasma-desktop")
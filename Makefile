# Makefile

SHELL	:= sh -e

SCRIPTS	:= contrib/*.sh

VERSION	:= $$(awk -F= '/X-KDE-PluginInfo-Version/ { print $$2 }' metadata.desktop)

all:	build

test:
	@echo -n "Checking for syntax errors"

	@for SCRIPT in $(SCRIPTS); \
	do \
		sh -n $${SCRIPT}; \
		echo -n "."; \
	done

	@echo " done."

	@if [ -x "$$(which checkbashisms 2>/dev/null)" ]; \
	then \
		echo -n "Checking for bashisms"; \
		for SCRIPT in $(SCRIPTS); \
		do \
			checkbashisms -f -x $${SCRIPT}; \
			echo -n "."; \
		done; \
		echo " done."; \
	else \
		echo "W: checkbashisms - command not found"; \
		echo "I: checkbashisms can be optained from: "; \
		echo "I:   http://git.debian.org/?p=devscripts/devscripts.git"; \
		echo "I: On Debian systems, checkbashisms can be installed with:"; \
		echo "I:   apt-get install devscripts"; \
	fi

build:
	sh Messages.sh

install:
	mkdir -p $(DESTDIR)/usr/share/kde4/apps/plasma/plasmoids/veromix-plasmoid
	cp -a contents dbus-service metadata.desktop $(DESTDIR)/usr/share/kde4/apps/plasma/plasmoids/veromix-plasmoid

	mkdir -p $(DESTDIR)/usr/share/dbus-1/services
	cp -a org.veromix.pulseaudio.service $(DESTDIR)/usr/share/dbus-1/services

	mkdir -p $(DESTDIR)/usr/share/kde4/services
	ln -s ../apps/plasma/plasmoids/veromix-plasmoid/metadata.desktop $(DESTDIR)/usr/share/kde4/services/plasma-widget-veromix.desktop

	mkdir -p $(DESTDIR)/usr/share/icons
	ln -s ../kde4/apps/plasma/plasmoids/veromix-plasmoid/contents/icons/veromix-plasmoid-128.png $(DESTDIR)/usr/share/icons/veromix-plasmoid.png

	# legacy hack for kde 4.4
	if [ "$$(kde4-config --kde-version | awk -F\. '{ print $$2 }')" -lt 5 ]; \
	then \
		sed -i -e 's|Plasma/Applet,Plasma/PopupApplet|Plasma/PopupApplet|' $(DESTDIR)/usr/share/kde4/apps/plasma/plasmoids/veromix-plasmoid/metadata.desktop ; \
	fi

clean:
	rm -rf .pc
	-find . -name '*~' | xargs rm -f
	-find . -name '*.pyc' | xargs rm -f
	-find contents/locale -name "*.mo" | xargs rm -f

distclean:	clean

dist:	clean
	tar cfzv ../plasma-widget-veromix_$(VERSION).orig.tar.gz --exclude=.svn --exclude=debian --exclude="contrib" ../$(shell basename $(CURDIR))

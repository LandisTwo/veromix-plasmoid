# Makefile

SHELL := sh -e

VERSION := $$(awk -F= '/X-KDE-PluginInfo-Version/ { print $$2 }' plasma/metadata.desktop)

_VEROMIX_SHARED := $(DESTDIR)/usr/share/veromix

all: build

build:
	@echo "sh Messages.sh"

install: install-plasmoid install-gtk

install-service:
	mkdir -p $(_VEROMIX_SHARED)
	cp -a dbus-service common $(_VEROMIX_SHARED)

	mkdir -p $(_VEROMIX_SHARED)/data
	cp -a data/icons data/presets $(_VEROMIX_SHARED)/data

	mkdir -p $(DESTDIR)/usr/share/dbus-1/services
	cp -a data/dbus-1/services/* $(DESTDIR)/usr/share/dbus-1/services

	mkdir -p $(DESTDIR)/usr/share/icons
	ln -s ../veromix/data/icons/veromix-plasmoid-128.png $(DESTDIR)/usr/share/icons/veromix-plasmoid.png
	ln -s ../veromix/data/icons/veromix-plasmoid-128.png $(DESTDIR)/usr/share/icons/veromix.png

install-plasmoid: install-service
	mkdir -p $(DESTDIR)/usr/share/kde4/apps/plasma/plasmoids/veromix-plasmoid
	cp -a plasma/contents plasma/metadata.desktop $(DESTDIR)/usr/share/kde4/apps/plasma/plasmoids/veromix-plasmoid

	mkdir -p $(DESTDIR)/usr/share/kde4/services
	ln -s ../apps/plasma/plasmoids/veromix-plasmoid/metadata.desktop $(DESTDIR)/usr/share/kde4/services/plasma-widget-veromix.desktop

install-gtk: install-service
	mkdir -p $(_VEROMIX_SHARED)
	cp -a gtk $(_VEROMIX_SHARED)

	mkdir -p $(DESTDIR)/usr/share/applications
	cp -a data/applications/veromix.desktop $(DESTDIR)/usr/share/applications

clean:
	-find . -name '*~' | xargs rm -f
	-find . -name '*.pyc' | xargs rm -f
	-find . -name '__pycache__' | xargs rm -f
	-find plasma/contents/locale -name "*.mo" | xargs rm -f

distclean: clean

dist: clean
	tar cfzv ../veromix_$(VERSION).orig.tar.gz --exclude=.git --exclude=debian --exclude="contrib" ../$(shell basename $(CURDIR))

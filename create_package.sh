#!/bin/sh
VERSION=$(cat metadata.desktop | grep X-KDE-PluginInfo-Version | awk 'BEGIN {FS= "="} ; { print $2 }')
NAME=$(date +'%Y-%m-%d')
NAME="${NAME}_${VERSION}_veromix.plasmoid"
TAR_NAME="../plasma-widget-veromix_$VERSION.orig.tar.gz"

find ./ -name '*~' | xargs rm
find ./ -name '*.pyc' | xargs rm
zip -r  ../$NAME * -x */*.svn/*
plasmapkg -u ../$NAME
rm $TAR_NAME
tar zcvf $TAR_NAME --exclude=.svn  --exclude=debian --exclude="*.sh" --exclude="metadata.desktop.kde4.4" --exclude="*.mo" .
echo $NAME


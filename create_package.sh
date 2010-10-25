#!/bin/bash
# rm *.
VERSION=`cat metadata.desktop | grep X-KDE-PluginInfo-Version | awk 'BEGIN {FS= "="} ; { print $2 }'`
NAME=`date +'%Y-%m-%d'`
NAME="${NAME}_${VERSION}_veromix.plasmoid"
find ./ -name '*~' | xargs rm
find ./ -name '*.pyc' | xargs rm
zip -r  ../$NAME * -x */*.svn/*
#plasmapkg -r veromix-plasmoid
plasmapkg -u ../$NAME
echo $NAME


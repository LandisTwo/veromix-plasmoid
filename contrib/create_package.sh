#!/bin/sh
VERSION=$(cat metadata.desktop | grep X-KDE-PluginInfo-Version | awk 'BEGIN {FS= "="} ; { print $2 }')
NAME=$(date +'%Y-%m-%d')
NAME="${NAME}_${VERSION}_veromix.plasmoid"
TAR_NAME="plasma-widget-veromix_$VERSION.orig.tar.gz"

find ./ -name '*~' | xargs rm
find ./ -name '*.pyc' | xargs rm
zip -r  ../$NAME * -x */*.svn/* debian\* contrib\* *.sh
plasmapkg -u ../$NAME
echo $NAME
ORIG=$(pwd)

TMPDIR=/tmp/debian
rm -rf "${TMPDIR}"
mkdir ${TMPDIR}
tar zcvf ${TMPDIR}/$TAR_NAME --exclude=.svn --exclude="*~^" --exclude="contrib" --exclude=debian --exclude="reload_plasma.sh"  --exclude="kill_service.sh" --exclude="create_package.sh"  --exclude="metadata.desktop.kde4.4" --exclude="*.mo" .

BUILDDIR=${TMPDIR}/plasma-widget-veromix
mkdir ${BUILDDIR}

CUR=$(pwd)
cd  ${BUILDDIR}
pwd
tar -xzf ${TMPDIR}/$TAR_NAME
cd ${CUR}
cp -r debian ${BUILDDIR}
find debian/ -type d -name '.svn' | xargs rm -rf
pwd

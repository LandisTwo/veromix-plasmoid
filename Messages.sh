#! /usr/bin/env bash
##
# copied from now-rocking plasmoid
##
NAME="veromix-plasmoid"
XGETTEXT="xgettext -ki18n"
EXTRACTRC="extractrc"

if [ "x$1" != "x" ]; then
    if [ ! -d "plasma/contents/locale/$1" ]; then
        mkdir -p "plasma/contents/locale/$1/LC_MESSAGES"
    fi
fi

$EXTRACTRC plasma/contents/ui/*.ui plasma/contents/config/*.xml > ./rc.py
$XGETTEXT rc.py plasma/contents/code/*.py plasma/contents/code/veromixcommon/*.py -o "$NAME.pot"
sed -e 's/charset=CHARSET/charset=UTF-8/g' -i "$NAME.pot"

for d in plasma/contents/locale/*; do
    if [ -d "$d" ]; then
        if [ -f "$d/LC_MESSAGES/$NAME.po" ]; then
            echo "Merging $NAME.pot -> $d/LC_MESSAGES/$NAME.po ..."
            msgmerge -U "$d/LC_MESSAGES/$NAME.po" "$NAME.pot"
        else
            echo "Copying $NAME.pot -> $d/LC_MESSAGES/$NAME.po ..."
            cp "$NAME.pot" "$d/LC_MESSAGES/$NAME.po"
        fi
    fi
done

for d in plasma/contents/locale/*; do
    echo "Making $d/LC_MESSAGES/$NAME.mo ..."
    msgfmt "$d/LC_MESSAGES/$NAME.po" -o "$d/LC_MESSAGES/$NAME.mo"
done

find . -name '*~' | xargs rm -f
rm -f rc.py
rm -f $NAME.pot

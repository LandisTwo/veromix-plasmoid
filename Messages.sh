#! /usr/bin/env bash
##
# copied from now-rocking plasmoid
##
NAME="veromix-plasmoid"
XGETTEXT="xgettext -ki18n"
EXTRACTRC="extractrc"

if [ "x$1" != "x" ]; then
    if [ ! -d "contents/locale/$1" ]; then
        mkdir -p "contents/locale/$1/LC_MESSAGES"
    fi
fi

$EXTRACTRC contents/ui/*.ui contents/config/*.xml > ./rc.py
$XGETTEXT rc.py contents/code/*.py -o "$NAME.pot"
sed -e 's/charset=CHARSET/charset=UTF-8/g' -i "contents/$NAME.pot"

for d in contents/locale/*; do
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

for d in contents/locale/*; do
    echo "Making $d/LC_MESSAGES/$NAME.mo ..."
    msgfmt "$d/LC_MESSAGES/$NAME.po" -o "$d/LC_MESSAGES/$NAME.mo"
done

rm -f rc.py
rm -f $NAME.pot

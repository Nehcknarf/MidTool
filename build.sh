#!/bin/bash

echo "Open project dir"
cd /mnt/e/PycharmProjects/midtool/ || exit

echo "QRC file generate"
pyside6-rcc resource.qrc -o src/resource.py

echo "Start building..."
pyinstaller src/main.py \
--noconfirm \
--add-data './lib:./lib' \
--add-data './script:./script' \
#--add-data './content:./content' \
#--add-data './imports:./imports' \
#--add-data './qtquickcontrols2.conf:./'
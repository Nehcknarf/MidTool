#!/bin/bash

echo "Open project dir"
cd /mnt/e/PycharmProjects/midtool/ || exit

echo "QRC file generate"
pyside6-rcc resource.qrc -o src/utils/resource.py

echo "Start building..."
pyinstaller src/main.py \
--noconfirm \
--name midtool2 \
--add-data './lib/fingerprint/*.so:./lib/fingerprint/' \
--add-data './script:./script' \
--add-data './i18n:./i18n' \
--add-data './content/images/icon.png:./' \
--add-data './lib/libpyside6qml.abi3.so.6.5:./' \
--collect-all tzdata \
--clean

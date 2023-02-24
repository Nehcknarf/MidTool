#!/bin/bash
echo "Activate conda env"
conda init bash
conda activate qt5

echo "Open project dir"
cd /mnt/c/Users/Nehcknarf/PycharmProjects/midtool/

echo "Start building..."
pyinstaller --noconfirm \
--add-data './midtool.ui:.' \
--add-data './icon.png:.' \
--add-data './virtualkeyboard/so:./Pyside2/Qt/plugins/virtualkeyboard' \
--add-data './lang:./lang' \
--add-data './libapit.so:.' \
--add-data './lib0a0.so:.' \
midtool.py

echo "remove previous version..."
sudo rm -rf /nubomed/*

echo "Start copying..."
sudo cp -r /mnt/c/Users/Nehcknarf/PycharmProjects/midtool/dist/midtool /nubomed
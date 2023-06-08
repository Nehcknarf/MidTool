#!/bin/bash
echo "Activate conda env"
conda init bash
conda activate qt5

echo "Open project dir"
cd /mnt/c/Users/Nehcknarf/PycharmProjects/midtool/

echo "Start building..."
pyinstaller --noconfirm \
--add-data './bin/linux/virtualkeyboard:./Pyside2/Qt/plugins/virtualkeyboard' \
--add-data './bin/linux/fingerprint:./bin/linux/fingerprint' \
--add-data './bin/icon/icon.png:.' \
--add-data './shell:./shell' \
midtool.py

echo "remove previous version..."
sudo rm -rf /nubomed/*

#echo "Start copying..."
#sudo cp -r /mnt/e/PycharmProjects/midtool/dist/midtool /nubomed
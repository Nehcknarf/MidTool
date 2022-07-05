# MidTool

MidTool@Qt 中台工具 GUI

打包命令：
pyinstaller --noconfirm \
--add-data './midtool.ui:.' \
--add-data './icon.png:.' \
--add-data './virtualkeyboard:./Pyside2/Qt/plugins/virtualkeyboard' \
--add-data './libapit.so:.' \
midtool.py

默认放置路径：
/nubomed/midtool

依赖：
sudo apt install libpulse-dev
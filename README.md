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

构建 Qt 应用依赖：
sudo apt install build-essential libgl1-mesa-dev
QtMultimedia 依赖：
sudo apt install libpulse-mainloop-glib0
Wayland 依赖
sudo apt install qtwayland5
X11 部分依赖
sudo apt install libxkbcommon-x11-0 libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-render-util0 libxcb-xinerama0 libxcb-xkb1
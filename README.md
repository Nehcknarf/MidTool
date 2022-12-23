# MidTool
MidTool 中台工具

## 开发环境
```
Python 3.10
PySide2 5.15.2.1
```

## Linux 版快捷打包脚本
`切换到相应的conda或pip环境下，执行./build.sh`

## Linux 版打包命令
```
pyinstaller --noconfirm \
--add-data './midtool.ui:.' \
--add-data './icon.png:.' \
--add-data './virtualkeyboard:./Pyside2/Qt/plugins/virtualkeyboard' \
--add-data './libapit.so:.' \
midtool.py
```

## Windows 版打包命令
`pyinstaller --noconfirm --noconsole --add-data ./midtool.ui;. --add-data ./icon.png;. --add-data ./libapit.dll;. --icon icon.png midtool.py`

## Linux 版默认放置路径
`/nubomed/midtool`

## 构建 Qt 应用依赖
`sudo apt install build-essential libgl1-mesa-dev`

## QtMultimedia 依赖
`sudo apt install libpulse-mainloop-glib0`

## Wayland 依赖
`sudo apt install qtwayland5`

## X11 依赖
`sudo apt install libxkbcommon-x11-0 libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-render-util0 libxcb-xinerama0 libxcb-xkb1`
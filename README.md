# MidTool
MidTool 中台工具

## 开发环境
```
Python 3.10
PySide2 5.15.2.1
```
## 构建 Qt 应用依赖
`sudo apt install build-essential libgl1-mesa-dev`

## QtMultimedia 依赖
[//]: # (`sudo apt install libpulse-mainloop-glib0`)
`sudo apt install libqt5multimedia5-plugins gstreamer1.0-plugins-bad`

## Wayland 依赖 (可选)
`sudo apt install qtwayland5`

## X11 依赖
`sudo apt install libxkbcommon-x11-0 libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-render-util0 libxcb-xinerama0`

## 创建并激活虚拟环境，安装依赖
```
conda create -n midtool python=3.10
conda activate midtool
pip install -r requirements.txt
```

## 将 qrc 资源文件编译到 py 文件
`pyside2-rcc -o qrc.py midtool.qrc`

## Qt 国际化
1. 执行 `pyside2-lupdate midtool.py midtool.ui -ts lang/zh_TW.ts`
2. 使用 Qt Linguist 打开zh_TW.ts，逐个添加译文
3. 发布

## Linux 版打包命令
```
pyinstaller --noconfirm \
--add-data './bin/linux/virtualkeyboard:./Pyside2/Qt/plugins/virtualkeyboard' \
--add-data './bin/linux/fingerprint:./bin/linux/fingerprint' \
--add-data './bin/icon/icon.png:.' \
--add-data './shell:./shell' \
midtool.py
```

## Linux 版快捷打包脚本
`切换到相应的conda或pip环境下，执行./build.sh`

## Linux 版默认放置路径
`/nubomed/midtool`

## Windows 版打包命令
`pyinstaller --noconfirm --noconsole --upx-dir ./upx --add-data ./bin/icon/icon.png;. --add-data ./bin/win/fingerprint;./bin/win/fingerprint --add-data ./bin/win/virtualkeyboard;./Pyside2/Qt/plugins/virtualkeyboard --icon icon.png midtool.py`

## Windows 版快捷打包脚本
`切换到相应的conda或pip环境下，执行./build.ps1`
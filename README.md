# MidTool
MidTool 中台工具

## 开发环境
```
Python 3.10
PySide2 5.15.2.1
```

## 创建并激活虚拟环境，安装依赖
```
conda create -n midtool python=3.10
conda activate midtool
pip install -r requirements.txt
```

## 构建 Qt 应用依赖
`sudo apt install build-essential libgl1-mesa-dev`

## X11 依赖
`sudo apt install libfontconfig1-dev libfreetype6-dev libx11-dev libx11-xcb-dev libxext-dev libxfixes-dev libxi-dev libxrender-dev libxcb1-dev libxcb-cursor-dev libxcb-glx0-dev libxcb-keysyms1-dev libxcb-image0-dev libxcb-shm0-dev libxcb-icccm4-dev libxcb-sync-dev libxcb-xfixes0-dev libxcb-shape0-dev libxcb-randr0-dev libxcb-render-util0-dev libxcb-util-dev libxcb-xinerama0-dev libxcb-xkb-dev libxkbcommon-dev libxkbcommon-x11-dev`

## Wayland 依赖 (可选)
`sudo apt install qtwayland5`

## QtMultimedia 依赖 (GStreamer + libpulse)
`sudo apt install libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev libgstreamer-plugins-bad1.0-dev gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly gstreamer1.0-libav gstreamer1.0-tools gstreamer1.0-x gstreamer1.0-alsa gstreamer1.0-gl gstreamer1.0-gtk3 gstreamer1.0-qt5 gstreamer1.0-pulseaudio libpulse-dev`

## 将 qrc 资源文件编译到 py 文件
`pyside2-rcc -o qrc.py midtool.qrc`

## Qt 国际化 (pyside2-lupdate 已过时且存在 bug，需使用 Qt 原生 lupdate 生成)
1. Win 环境为例，打开目录 ` C:\Qt\版本号\mingw_64\bin`
2. 单击右键，运行终端，执行命令 `.\lupdate E:\PycharmProjects\midtool\i18n.pro` (需按照仓库实际位置替换路径)
3. 使用目录下的 linguist.exe 打开生成的 *.ts，逐个添加译文后发布

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
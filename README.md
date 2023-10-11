# MidTool 2
MidTool 中台工具 Qt6 + QML 重构版本

## 开发环境
```
Python 3.11
PySide6 6.5
```

## 开发IDE
```
PyCharm 2023.2 Pro 用于主力开发，从该版本开始支持QML语法检查
Qt Design Studio 4.2 该IDE只能生成C++项目，Python无法直接套用。此IDE仅用于QML控件可视化调试，后将代码复制到QML文件中进行后续开发。
Qt Creator 11 可用于QML调试
```

## 创建并激活虚拟环境，安装依赖
```
conda create -n midtool python=3.11
conda activate midtool
pip install -r requirements.txt
```

## 构建 Qt 应用依赖
`sudo apt install build-essential libgl1-mesa-dev`

## X11 依赖
`sudo apt install libfontconfig1-dev libfreetype6-dev libx11-dev libx11-xcb-dev libxext-dev libxfixes-dev libxi-dev libxrender-dev libxcb1-dev libxcb-cursor-dev libxcb-glx0-dev libxcb-keysyms1-dev libxcb-image0-dev libxcb-shm0-dev libxcb-icccm4-dev libxcb-sync-dev libxcb-xfixes0-dev libxcb-shape0-dev libxcb-randr0-dev libxcb-render-util0-dev libxcb-util-dev libxcb-xinerama0-dev libxcb-xkb-dev libxkbcommon-dev libxkbcommon-x11-dev`

## Qt6 Multimedia 后端依赖
`sudo apt install ffmpeg`

## 将 qrc 资源文件编译到 py 文件
`pyside6-rcc resource.qrc -o src/utils/resource.py`

## 配置 Pycharm 显示 QML Debug 输出到控制台的方法
```
在 Pycharm 的 Run/Debug Configurations 设置中，找到 Modify options 下拉菜单，勾选 Emulate terminal in output console
```

## Ubuntu 20.04 开发环境运行问题踩坑
```
相关问题：libGL error: MESA-LOADER: failed to open swrast: /usr/lib/dri/swrast_dri.so: cannot open shared object file: No such file or directory (search paths /usr/lib/x86_64-linux-gnu/dri:\$${ORIGIN}/dri:/usr/lib/dri, suffix _dri)
解决方式：添加环境变量，在 Pycharm 的 Run/Debug Configurations 设置中，向 Environment variables 添加 LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libffi.so.7，即可在 Ubuntu 20.04 开发环境下即时运行程序。Ubuntu 22.04 没有该问题，无需执行上述配置。
```

## Ubuntu 22.04 打包问题踩坑
```
相关问题：https://github.com/pyinstaller/pyinstaller/issues/7197
解决方式：升级 Ubuntu 22.04，获得最新的 glibc 修复
```

## Linux 下 QML Camera 开启后关闭，无法再次打开的问题
```
关联BUG：https://bugreports.qt.io/browse/QTBUG-116470
解决方式：疑似为 PySide6 6.5 小版本引入的 BUG，等待 Qt 官方修复 BUG
```
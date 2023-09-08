# MidTool 2
MidTool 中台工具 Qt6 + QML 重构版本

## 开发环境
```
Python 3.11
PySide6 6.5.2
```

## 开发IDE
```
Qt Design Studio 4.2 该IDE只能生成C++项目，Python无法直接套用。此IDE仅用于QML控件可视化调试，后将代码复制到QML文件中进行后续开发
Qt Creator 11 用于QML调试
PyCharm 2023.2.1 主力开发
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

## Ubuntu 20.04 开发环境问题踩坑
```
libGL error: MESA-LOADER: failed to open swrast: /usr/lib/dri/swrast_dri.so: cannot open shared object file: No such file or directory (search paths /usr/lib/x86_64-linux-gnu/dri:\$${ORIGIN}/dri:/usr/lib/dri, suffix _dri)
解决方式：创建软链接
mkdir -p /usr/lib/dri/
sudo ln -s /usr/lib/x86_64-linux-gnu/dri/swrast_dri.so /usr/lib/dri/
```

## Ubuntu 22.04 开发环境问题踩坑
```
https://github.com/pyinstaller/pyinstaller/issues/7197
解决方式：创建软链接
sudo find / -name libpyside6qml*
sudo ln -s /home/z/miniconda3/envs/midtoolNext2204/lib/python3.11/site-packages/PySide6/libpyside6qml.abi3.so.6.5 /lib
```
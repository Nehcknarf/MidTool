# MidTool 2
### MidTool 中台工具箱 重构版本 
### 基于 Qt6.5 LTS，前端由 QML 编写，后端为 PySide6

## 开发环境
| Pack    | Version |
|---------|---------|
| Python  | 3.11    |
| PySide6 | 6.5     |

## 可用的IDE
- PyCharm 2023.2 (Professional Edition)
  - 用于主力开发，从该版本开始支持QML语法检查
- Qt Design Studio 4.2 
  - 该IDE只能生成C++项目，Python无法直接套用。此IDE仅用于QML控件可视化调试，后将代码复制到QML文件中进行后续开发。
- Qt Creator 11 
  - 可用于QML调试

## 创建并激活虚拟环境，安装依赖包
```
conda create -n midtool python=3.11
conda activate midtool
pip install -r requirements.txt
```

## pkg 依赖
### 构建 Qt 应用依赖
`sudo apt install build-essential libgl1-mesa-dev`
### X11 依赖
`sudo apt install libfontconfig1-dev libfreetype6-dev libx11-dev libx11-xcb-dev libxext-dev libxfixes-dev libxi-dev libxrender-dev libxcb1-dev libxcb-cursor-dev libxcb-glx0-dev libxcb-keysyms1-dev libxcb-image0-dev libxcb-shm0-dev libxcb-icccm4-dev libxcb-sync-dev libxcb-xfixes0-dev libxcb-shape0-dev libxcb-randr0-dev libxcb-render-util0-dev libxcb-util-dev libxcb-xinerama0-dev libxcb-xkb-dev libxkbcommon-dev libxkbcommon-x11-dev`
### Qt6 Multimedia 后端依赖
`sudo apt install ffmpeg`

## QRC 编译
### 将 qrc 资源文件编译到 py 文件, 每次更新前端源码后需要执行此步才能生效
`pyside6-rcc resource.qrc -o src/utils/resource.py`

## 踩坑
### 配置 Pycharm 显示 QML Debug 输出到控制台的方法
```
在 Pycharm 的 Run/Debug Configurations 设置中，找到 Modify options 下拉菜单，勾选 Emulate terminal in output console
```
### Ubuntu 20.04 开发环境运行问题踩坑
```
相关问题：libGL error: MESA-LOADER: failed to open swrast: /usr/lib/dri/swrast_dri.so: cannot open shared object file: No such file or directory (search paths /usr/lib/x86_64-linux-gnu/dri:\$${ORIGIN}/dri:/usr/lib/dri, suffix _dri)
解决方式：添加环境变量，在 Pycharm 的 Run/Debug Configurations 设置中，向 Environment variables 添加 LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libffi.so.7，即可在 Ubuntu 20.04 开发环境下即时运行程序。Ubuntu 22.04 没有该问题，无需执行上述配置。
```
### Ubuntu 22.04 打包问题踩坑
```
相关问题：https://github.com/pyinstaller/pyinstaller/issues/7197
解决方式：升级 Ubuntu 22.04，获得最新的 glibc 修复
```

## 已知问题
### Linux 下 QML Camera 开启后关闭，无法再次打开相机，提示 Camera is in use
```
关联BUG：https://bugreports.qt.io/browse/QTBUG-117735
线索：Qt 6.5 小版本更新引入的 BUG，Qt 官方宣称会在 6.5.4 版本中修复，但是从 6.5.4 开始仅面向商业客户提供，所以可能不会放出 PySide6 6.5.4 安装包
```

## 编译打包
```先切换至 midtool 虚拟环境，打开项目目录，执行 ./build.sh，编译前如需更新版本号，请编辑 src/utils/version.py 中 midtool_version 变量```
# MidTool - R2000可视化运维工具
### MidTool 工具箱 重构版本

## 可用 IDE
- PyCharm 2023.2 (Professional Edition)
  - 主力开发，从该版本开始支持 QML 语法检查
- Qt Design Studio
  - 虽然只能创建 C++ 项目，但是能够可视化绘制 QML 控件。可将由绘制生成的代码复制到项目的 QML 文件中进行后续开发。

## 开发环境
### Windows 11 下推荐使用 WSL Ubuntu 20.04 开发 (理论上编译出的应用向后兼容)
### 基于 Qt6.8 LTS，前端由 QML 语言编写，后端为 PySide6
| Pack    | Version |
|---------|---------|
| Python  | 3.13    |
| PySide6 | 6.8.3   |

## 快速开始
### 安装运行&编译依赖包（包含构建 Qt 应用基础依赖、X11 依赖）
```bash
sudo apt install -y libgl1-mesa-dev libfontconfig1-dev libfreetype-dev libgtk-3-dev libx11-dev libx11-xcb-dev libxcb-cursor-dev libxcb-glx0-dev libxcb-icccm4-dev libxcb-image0-dev libxcb-keysyms1-dev libxcb-randr0-dev libxcb-render-util0-dev libxcb-shape0-dev libxcb-shm0-dev libxcb-sync-dev libxcb-util-dev libxcb-xfixes0-dev libxcb-xkb-dev libxcb1-dev libxext-dev libxfixes-dev libxi-dev libxkbcommon-dev libxkbcommon-x11-dev libxrender-dev
```
### 创建&激活虚拟环境，安装项目依赖（Qt6 Multimedia 后端依赖 FFmpeg；Deepin 23 国产操作系统需要使用 Python 3.12）
```bash
conda create -n midtool python=3.13
conda activate midtool
conda install c-compiler cxx-compiler ffmpeg
pip install -r requirements.txt
```

## 编译
### 单独编译 qrc（将 qrc 资源文件编译到 py 文件, 每次更新 QML 前端源码后需要执行此步才能生效）
- 激活虚拟环境，执行 `pyside6-rcc resource.qrc -o src/utils/resource.py`
### 打包发布
- 发布前如需更新版本号，请编辑 src/utils/version.py 中 midtool_version 变量
1. 执行 `conda activate midtool` 激活 midtool 虚拟环境，
2. 切换到项目根目录
3. 执行 `bash build.sh`，执行完毕会在根目录dist文件夹下生成新构建的程序包

## 踩坑
### 配置 Pycharm 将 QML Debug 信息输出到控制台的方法
```
在 Pycharm 的 Run/Debug Configurations 设置中，找到 Modify options 下拉菜单，勾选 Emulate terminal in output console
```
### Ubuntu 20.04 IDE即时运行问题踩坑
```
问题：libGL error: MESA-LOADER: failed to open swrast: /usr/lib/dri/swrast_dri.so: cannot open shared object file: No such file or directory (search paths /usr/lib/x86_64-linux-gnu/dri:\$${ORIGIN}/dri:/usr/lib/dri, suffix _dri)
解决方式：添加环境变量，在 Pycharm 的 Run/Debug Configurations 设置中，向 Environment variables 添加 LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libffi.so.7
```

## 已知问题
### ~~Linux 下 QML Camera 开启后关闭，无法再次打开相机，提示 Camera is in use~~ 由于已经迁移到 Qt6.8，已无此问题
```
关联BUG：https://bugreports.qt.io/browse/QTBUG-117735
线索：Qt BUG，官方已在 6.5.4 中修复，但是从 6.5.4 开始仅面向商业客户提供 wheel，免费用户无法获得更新，除非升级非 LTS 版本，可能会引入其他不稳定因素，暂不考虑。
```
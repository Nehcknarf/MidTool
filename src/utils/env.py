import os
import sys
import platform
from pathlib import Path


# midtool running path
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    root_path = sys._MEIPASS
else:
    root_path = Path(__file__).parents[2]

# Middleware path
consumable_cabinet_path = "/nubomed/consumable-cabinet-service/"
drug_cabinet_path = "/nubomed/midpkg/drug-middleware/"
ecart_path = "/nubomed/ecart-service/"

# Product
if Path(consumable_cabinet_path).exists():
    # 耗材
    product_type = 0
    middleware_root_path = Path(consumable_cabinet_path)
elif Path(drug_cabinet_path).exists():
    # 药品
    product_type = 1
    middleware_root_path = Path(drug_cabinet_path)
elif Path(ecart_path).exists():
    # 抢救车
    product_type = 2
    middleware_root_path = Path(ecart_path)
else:
    # 未知设备
    product_type = -1
    middleware_root_path = Path(".")

# Middleware sub folder
middleware_cfg_path = middleware_root_path / "conf"
middleware_log_path = middleware_root_path / "logs"
# Middleware config file
sync_cfg_path = middleware_cfg_path / "application-sync.yml"
nvr_cfg_path = middleware_cfg_path / "application-nvr.yml"
extern_cfg_path = middleware_cfg_path / "application-extern.yml"
ws_cfg_path = middleware_cfg_path / "application-ws.yml"
mcc_cfg_path = middleware_cfg_path / "application-mcc.yml"
action_delay_cfg_path = middleware_cfg_path / "application-action-delay.yml"

# System
system = platform.system()

if system == "Linux":
    # For Shell
    user = os.environ.get("USER")
    work_path = f"/home/{user}"
    shell = "/bin/bash -c \"{}\""
    coding = "UTF-8"
    sep = "\n"
    # For running
    ubuntu_version = platform.freedesktop_os_release()["VERSION_ID"]

    if ubuntu_version == "22.04":
        # Ubuntu 22.04 下 Qt Wayland 程序无法拖拽窗口，属于系统bug，故先使用 X11
        # os.environ["QT_QPA_PLATFORM"] = "wayland"
        os.environ["QT_QPA_PLATFORM"] = "xcb"
    elif ubuntu_version == "20.04":
        os.environ["QT_QPA_PLATFORM"] = "xcb"

elif system == "Windows":
    # For Shell
    user = os.environ.get("UserName")
    work_path = f"C:/Users/{user}"
    shell = "powershell {}"
    coding = "GBK"
    sep = "\r\n"

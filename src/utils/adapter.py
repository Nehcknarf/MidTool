import os
import sys
import platform
import tomllib
from pathlib import Path
from datetime import datetime


# MidTool running path
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    root_path = sys._MEIPASS
    build_date = datetime.fromtimestamp(os.path.getmtime(sys.executable)).strftime('%Y-%m-%d')
else:
    root_path = Path(__file__).parents[2]
    build_date = datetime.now().strftime("%Y-%m-%d")

# Middleware path
with open(f"{root_path}/config/config.toml", "rb") as f:
    cfg = tomllib.load(f)

    consumable_cabinet_path = cfg["consumable_cabinet"]["path"]
    drug_cabinet_path = cfg["drug_cabinet"]["path"]
    ecart_path = cfg["ecart"]["path"]

    consumable_cabinet_cfg = cfg["consumable_cabinet"]["mid_cfg"]
    ecart_cfg = cfg["ecart"]["mid_cfg"]

    consumable_cabinet_service = cfg["consumable_cabinet"]["service"]
    ecart_service = cfg["ecart"]["service"]

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
middleware_cfg_path = middleware_root_path / cfg["common"]["conf_dir"]
middleware_log_path = middleware_root_path / cfg["common"]["log_dir"]
# Config file
sync_cfg_path = middleware_cfg_path / cfg["common"]["sync_cfg"]
nvr_cfg_path = middleware_cfg_path / cfg["common"]["nvr_cfg"]
extern_cfg_path = middleware_cfg_path / cfg["common"]["extern_cfg"]
ws_cfg_path = middleware_cfg_path / cfg["common"]["ws_cfg"]
mcc_cfg_path = middleware_cfg_path / cfg["common"]["mcc_cfg"]
action_delay_cfg_path = middleware_cfg_path / cfg["common"]["action_delay_cfg"]
finger_cfg_path = middleware_cfg_path / cfg["ecart"]["finger_cfg"]
lang_cfg_path = middleware_cfg_path / cfg["ecart"]["lang_cfg"]

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

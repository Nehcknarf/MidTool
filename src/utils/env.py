import os
import platform
from pathlib import Path


root_path = Path(__file__).parent.parent.parent

system = platform.system()

if system == "Linux":
    # For Shell
    user = os.environ.get("USER")
    work_path = f"/home/{user}"
    shell = "/bin/bash -c \"{}\""
    coding = "UTF-8"
    sep = "\n"
    # For running
    os.environ["QT_QPA_PLATFORM"] = "xcb"

elif system == "Windows":
    # For Shell
    user = os.environ.get("UserName")
    work_path = f"C:/Users/{user}"
    shell = "powershell {}"
    coding = "GBK"
    sep = "\r\n"
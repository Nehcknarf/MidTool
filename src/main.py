import os
import sys

from PySide6.QtCore import QUrl, QLocale
from PySide6.QtGui import QGuiApplication, QIcon
from PySide6.QtQml import QQmlApplicationEngine

import utils.resource
from utils.translator import JsonTranslator
from utils.env import root_path

# 导入需要在QML中实例化的类
from monitoring import SystemInfoModel
from maintenance import Maintenance
from serial import Serial
from fingerprint import SquareFingerPrint, RoundFingerPrint
from camera import CameraModel
from editor import ConfigEditor
from activation import Activation
from network import Network
from timezone import TimeEditor


def set_qt_environment():
    os.environ["QT_IM_MODULE"] = "qtvirtualkeyboard"
    os.environ["QT_VIRTUALKEYBOARD_DESKTOP_DISABLE"] = "1"
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
    os.environ["QT_QUICK_CONTROLS_CONF"] = f"{root_path}/qtquickcontrols2.conf"
    os.environ["QT_DEBUG_PLUGINS"] = "0"
    os.environ["QT_MEDIA_BACKEND"] = "ffmpeg"


def main():
    set_qt_environment()

    app = QGuiApplication(sys.argv)
    app.setWindowIcon(QIcon(":/content/images/icon.png"))

    translator = JsonTranslator(app)
    if QLocale.system().name() == "zh_CN":
        translator.load(f"{root_path}/i18n/zh_CN.json")
    elif QLocale.system().name() == "zh_TW":
        translator.load(f"{root_path}/i18n/zh_TW.json")
    app.installTranslator(translator)

    engine = QQmlApplicationEngine()

    url = QUrl("qrc:/content/App.qml")

    # def handle_object_created(obj, obj_url):
    #     if obj is None and url == obj_url:
    #         QCoreApplication.exit(-1)
    #
    # engine.objectCreated.connect(handle_object_created, Qt.QueuedConnection)

    engine.addImportPath("qrc:/imports")
    # print(engine.importPathList())

    engine.load(url)

    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

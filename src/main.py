import os
import sys

from PySide6.QtCore import QUrl, QLocale, QCommandLineParser, QCommandLineOption
from PySide6.QtGui import QGuiApplication, QIcon
from PySide6.QtQml import QQmlApplicationEngine

import utils.resource
from utils.translator import JsonTranslator
from utils.adapter import root_path, product_type
from utils.version import midtool_version, python_version, qt_version

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
from downloader import LogDownloader


def set_qt_environment():
    os.environ["QT_IM_MODULE"] = "qtvirtualkeyboard"
    os.environ["QT_VIRTUALKEYBOARD_DESKTOP_DISABLE"] = "1"
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
    os.environ["QT_MEDIA_BACKEND"] = "ffmpeg"
    os.environ["QT_DEBUG_PLUGINS"] = "0"


def parse_args(app):
    tab_nickname_dict = {
        "Monitoring": 0,
        "Maintenance": 1,
        "Editor": 2,
        "Serial": 3,
        "Fingerprint": 4,
        "Face": 5,
        "Camera": 6,
        "Network": 7,
        "Time": 8,
        "LogDownload": 9
    }

    parser = QCommandLineParser()
    tab = QCommandLineOption(["t", "tab"], "Choice which tab to be shown at start up", "tab")
    parser.addOption(tab)
    parser.process(app)
    tab = parser.value(tab)
    if tab:
        index = tab_nickname_dict.get(tab)
        return index


def main():
    set_qt_environment()

    app = QGuiApplication(sys.argv)
    app.setWindowIcon(QIcon(":/content/images/icon.png"))

    translator = JsonTranslator(app)
    locale = QLocale.system().name()
    if locale == "zh_CN":
        translator.load(f"{root_path}/i18n/zh_CN.json")
    elif locale == "zh_TW":
        translator.load(f"{root_path}/i18n/zh_TW.json")
    app.installTranslator(translator)

    idx = parse_args(app)

    engine = QQmlApplicationEngine()

    url = QUrl("qrc:/content/App.qml")

    # def handle_object_created(obj, obj_url):
    #     if obj is None and url == obj_url:
    #         QCoreApplication.exit(-1)
    #
    # engine.objectCreated.connect(handle_object_created, Qt.QueuedConnection)

    engine.addImportPath("qrc:/imports")
    # print(engine.importPathList())

    engine.rootContext().setContextProperty("productType", product_type)
    engine.rootContext().setContextProperty("argCurrentIndex", idx)
    engine.rootContext().setContextProperty("midToolVersion", midtool_version)
    engine.rootContext().setContextProperty("pythonVersion", python_version)
    engine.rootContext().setContextProperty("qtVersion", qt_version)

    engine.load(url)

    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

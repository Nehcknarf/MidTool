import os
import sys

from PySide6.QtGui import QGuiApplication, QIcon
from PySide6.QtNetwork import QLocalSocket, QLocalServer
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QUrl, QLocale, QCommandLineParser, QCommandLineOption

import utils.resource
from utils.translator import JsonTranslator
from utils.adapter import root_path, product_type, build_date
from utils.version import midtool_version, python_version, qt_version

# 导入需要在QML中实例化的类
from monitoring import SystemInfoModel
from maintenance import Maintenance
from editor import ConfigEditor
from serial import Serial
from fingerprint import SquareFingerPrint, RoundFingerPrint
from activation import Activation
from camera import CameraModel
from network import Network
from timezone import TimeEditor
from downloader import LogDownloader
from reader import Reader


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
        "Reader": 5,
        "Face": 6,
        "Camera": 7,
        "Network": 8,
        "Time": 9,
        "LogDownload": 10
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

    # 防止多开
    server_name = "MidTool"
    socket = QLocalSocket()
    socket.connectToServer(server_name)

    if socket.waitForConnected(500):
        sys.exit(-1)
    else:
        local_server = QLocalServer()
        local_server.listen(server_name)

        translator = JsonTranslator(app)
        locale = QLocale.system().name()
        if locale == "zh_CN":
            translator.load(f"{root_path}/i18n/zh_CN.json")
        elif locale in ["zh_TW", "zh_HK", "zh_MO"]:
            translator.load(f"{root_path}/i18n/zh_TW.json")
        app.installTranslator(translator)

        idx = parse_args(app)

        engine = QQmlApplicationEngine()

        url = QUrl("qrc:/content/App.qml")

        engine.addImportPath("qrc:/imports")
        # print(engine.importPathList())

        context = engine.rootContext()
        context.setContextProperty("productType", product_type)
        context.setContextProperty("argCurrentIndex", idx)
        context.setContextProperty("midToolVersion", midtool_version)
        context.setContextProperty("buildDate", build_date)
        context.setContextProperty("pythonVersion", python_version)
        context.setContextProperty("qtVersion", qt_version)

        engine.load(url)

        if not engine.rootObjects():
            sys.exit(-1)

        sys.exit(app.exec())


if __name__ == "__main__":
    main()

import os
import sys

from PySide6.QtCore import QCoreApplication, Qt, QUrl
from PySide6.QtGui import QGuiApplication, QIcon, QFontDatabase, QFont
from PySide6.QtQml import QQmlApplicationEngine

# 导入需要在QML中实例化的类
from process import Process
from monitoring import SystemInfoModel
from maintenance import Maintenance
from serial import Serial
from fingerprint import SquareFingerPrint, RoundFingerPrint
from camera import CameraModel
from editor import ConfigEditor


def set_qt_environment():
    os.environ["QT_IM_MODULE"] = "qtvirtualkeyboard"
    os.environ["QT_VIRTUALKEYBOARD_DESKTOP_DISABLE"] = "1"
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
    os.environ["QT_LOGGING_RULES"] = "qt.qml.connections=false"
    os.environ["QT_QUICK_CONTROLS_CONF"] = "../qtquickcontrols2.conf"
    os.environ["QML_COMPAT_RESOLVE_URLS_ON_ASSIGNMENT"] = "1"
    # os.environ["QT_QPA_PLATFORM"] = "xcb"
    os.environ["QT_DEBUG_PLUGINS"] = "0"


def main():
    set_qt_environment()

    app = QGuiApplication(sys.argv)
    app.setWindowIcon(QIcon("../content/images/icon.png"))

    engine = QQmlApplicationEngine()

    url = QUrl("../main.qml")

    # font_id = QFontDatabase.addApplicationFont("../content/fonts/OPlusSans3-Medium.ttf")
    # font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
    # app.setFont(QFont(font_family))

    # def handle_object_created(obj, obj_url):
    #     if obj is None and url == obj_url:
    #         QCoreApplication.exit(-1)
    #
    # engine.objectCreated.connect(handle_object_created, Qt.QueuedConnection)

    engine.addImportPath("../imports")
    engine.addImportPath("../content")
    # print(engine.importPathList())

    engine.load(url)

    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

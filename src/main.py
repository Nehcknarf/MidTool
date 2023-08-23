import os
import sys

from PySide6.QtCore import QCoreApplication, Qt, QUrl, QObject
from PySide6.QtGui import QGuiApplication, QFontDatabase, QFont
from PySide6.QtQml import QQmlApplicationEngine

from camera import CameraModel
from process import Process
from system import SystemInfoModel
from fingerprint import SquareFingerPrint, RoundFingerPrint


def set_qt_environment():
    os.environ["QT_IM_MODULE"] = "qtvirtualkeyboard"
    os.environ["QT_VIRTUALKEYBOARD_DESKTOP_DISABLE"] = "1"
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
    os.environ["QT_LOGGING_RULES"] = "qt.qml.connections=false"
    os.environ["QT_QUICK_CONTROLS_CONF"] = "../qtquickcontrols2.conf"
    os.environ["QML_COMPAT_RESOLVE_URLS_ON_ASSIGNMENT"] = "1"
#    os.environ["QT_QPA_PLATFORM"] = "xcb"
    os.environ["QT_DEBUG_PLUGINS"] = "0"


class MidTool(QObject):
    def __init__(self):
        super().__init__()
        set_qt_environment()

        app = QGuiApplication(sys.argv)
        self.engine = QQmlApplicationEngine()

        url = QUrl("../content/App.qml")

        # font_id = QFontDatabase.addApplicationFont("../content/fonts/OPlusSans3-Medium.ttf")
        # font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        # app.setFont(QFont(font_family))

        def handle_object_created(obj, obj_url):
            if obj is None and url == obj_url:
                QCoreApplication.exit(-1)

        self.engine.objectCreated.connect(handle_object_created, Qt.QueuedConnection)

        self.engine.addImportPath("../imports")
        self.engine.addImportPath("../content")
        # print(engine.importPathList())

        self.engine.load(url)

        if not self.engine.rootObjects():
            sys.exit(-1)
        sys.exit(app.exec())


if __name__ == "__main__":
    MidTool()

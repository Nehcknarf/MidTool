import os
import sys

from PySide6.QtCore import QCoreApplication, Qt, QUrl, QThreadPool
from PySide6.QtGui import QGuiApplication, QFontDatabase, QFont
from PySide6.QtQml import QQmlApplicationEngine, qmlRegisterType

from camera import Camera
from process import Commander


threadpool = QThreadPool.globalInstance()


def set_qt_environment():
    os.environ["QT_IM_MODULE"] = "qtvirtualkeyboard"
    os.environ["QT_VIRTUALKEYBOARD_DESKTOP_DISABLE"] = "1"
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
    os.environ["QT_LOGGING_RULES"] = "qt.qml.connections=false"
    os.environ["QT_QUICK_CONTROLS_CONF"] = "../qtquickcontrols2.conf"
    os.environ["QML_COMPAT_RESOLVE_URLS_ON_ASSIGNMENT"] = "1"
    # os.environ["QT_QPA_PLATFORM"] = "xcb"
    os.environ["QT_DEBUG_PLUGINS"] = "1"


if __name__ == "__main__":
    set_qt_environment()

    app = QGuiApplication(sys.argv)

    engine = QQmlApplicationEngine()

    url = QUrl("../content/App.qml")

    # font_id = QFontDatabase.addApplicationFont("../content/fonts/OPlusSans3-Medium.ttf")
    # font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
    # app.setFont(QFont(font_family))

    engine.rootContext().setContextProperty("cameraListModel", Camera().camera_list)

    def handle_object_created(obj, obj_url):
        if obj is None and url == obj_url:
            QCoreApplication.exit(-1)

    engine.objectCreated.connect(handle_object_created, Qt.QueuedConnection)

    engine.addImportPath("../imports")
    engine.addImportPath("../content")
    # print(engine.importPathList())

    engine.load(url)

    # c = Commander("echo 1 | sudo -S ls")
    # c.run()
    # threadpool.start(c)

    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec())

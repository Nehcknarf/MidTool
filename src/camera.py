from PySide6.QtCore import QObject, Property
from PySide6.QtMultimedia import QMediaDevices
from PySide6.QtQml import QmlElement


QML_IMPORT_NAME = "src.camera"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0


@QmlElement
class CameraModel(QObject):
    cameraChanged = QMediaDevices.videoInputsChanged

    def get_cams(self):
        camera_model = [{"value": camera, "text": camera.description()} for camera in QMediaDevices.videoInputs()]
        return camera_model

    cameras = Property(list, get_cams, notify=cameraChanged)

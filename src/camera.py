from PySide6.QtMultimedia import QMediaDevices


class Camera(object):
    camera_list = [{"value": cam, "text": cam.description()} for cam in QMediaDevices.videoInputs()]

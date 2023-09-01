from pathlib import Path

from PySide6.QtCore import QObject, Property, Signal
from PySide6.QtQml import QmlElement


QML_IMPORT_NAME = "src.maintenance"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0


@QmlElement
class Maintenance(QObject):
    cabinetsChanged = Signal()

    def get_cabinets(self):
        p = Path("/nubomed/Device_defaultconf")
        if p.exists():
            return [x.name for x in p.iterdir() if x.is_dir()]

    cabinets = Property(list, get_cabinets, notify=cabinetsChanged)

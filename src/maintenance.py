import glob
import re

from PySide6.QtCore import QObject, Property, Signal
from PySide6.QtQml import QmlElement


QML_IMPORT_NAME = "src.maintenance"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0


@QmlElement
class Maintenance(QObject):
    cabinetsChanged = Signal()

    def get_cabinets(self):
        if install_sh := glob.glob("/nubomed/consumable-cabinet-service_V*/install.sh"):
            with open(install_sh[0], "r") as f:
                result = re.findall(r'echo "(\d{1,2}).+（(.+)）"', f.read())

            cabinets_model = []
            for i in result:
                cabinets_model.append({"text": i[1], "value": int(i[0])})
            return cabinets_model

    cabinets = Property(list, get_cabinets, notify=cabinetsChanged)

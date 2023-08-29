import psutil

from PySide6.QtCore import QAbstractListModel, QByteArray, Qt, QModelIndex, Slot
from PySide6.QtQml import QmlElement


QML_IMPORT_NAME = "src.monitoring"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0


@QmlElement
class SystemInfoModel(QAbstractListModel):
    NameRole = Qt.UserRole + 1
    PercentRole = Qt.UserRole + 2

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.system_info_model = []

    def rowCount(self, parent=QModelIndex()):
        return len(self.system_info_model)

    def data(self, index, role: int):
        if not self.system_info_model:
            ret = None
        elif not index.isValid():
            ret = None
        elif role == self.NameRole:
            ret = self.system_info_model[index.row()]["name"]
        elif role == self.PercentRole:
            ret = self.system_info_model[index.row()]["percent"]
        else:
            ret = None
        return ret

    def roleNames(self):
        default = super().roleNames()
        default[self.NameRole] = QByteArray(b"name")
        default[self.PercentRole] = QByteArray(b"percent")
        return default

    @Slot()
    def set_data(self):
        self.beginResetModel()
        self.get_system_info_model()
        self.endResetModel()
        return True

    def get_system_info_model(self):
        cpu_percent = psutil.cpu_percent()
        memory_percent = psutil.virtual_memory().percent
        disk_percent = psutil.disk_usage('/').percent

        self.system_info_model = [
            {"name": "CPU", "percent": format(cpu_percent, ".1f")},
            {"name": "Memory", "percent": format(memory_percent, ".1f")},
            {"name": "Disk", "percent": format(disk_percent, ".1f")}
        ]

import psutil

from PySide6.QtCore import QAbstractListModel, QByteArray, Qt, QModelIndex, Slot
from PySide6.QtQml import QmlElement

from process import Process
from utils.log import logger


QML_IMPORT_NAME = "src.monitoring"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0


@QmlElement
class MiddlewareManager(Process):
    @Slot()
    def start_middleware(self):
        logger.info("Start middleware...")
        self.start(f"pm2 start all")

    @Slot()
    def restart_middleware(self):
        logger.info("Restart middleware...")
        self.start(f"pm2 restart all")

    @Slot()
    def stop_middleware(self):
        logger.info("Stop middleware...")
        self.start(f"pm2 stop all")


@QmlElement
class SystemInfoModel(QAbstractListModel):
    NameRole = Qt.UserRole + 1
    StatusRole = Qt.UserRole + 2
    ProgressRole = Qt.UserRole + 3

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
        elif role == self.StatusRole:
            ret = self.system_info_model[index.row()]["status"]
        elif role == self.ProgressRole:
            ret = self.system_info_model[index.row()]["progress"]
        else:
            ret = None
        return ret

    def roleNames(self):
        default = super().roleNames()
        default[self.NameRole] = QByteArray(b"name")
        default[self.StatusRole] = QByteArray(b"status")
        default[self.ProgressRole] = QByteArray(b"progress")
        return default

    @Slot()
    def set_data(self):
        self.beginResetModel()
        self.get_system_info_model()
        self.endResetModel()

    def get_system_info_model(self):
        cpu_percent = f"{psutil.cpu_percent():.1f}"
        memory_percent = f"{psutil.virtual_memory().percent:.1f}"
        disk_percent = f"{psutil.disk_usage('/').percent:.1f}"

        self.system_info_model = [
            {"name": self.tr("CPU"), "status": cpu_percent, "progress": cpu_percent},
            {"name": self.tr("Memory"), "status": memory_percent, "progress": memory_percent},
            {"name": self.tr("Disk"), "status": disk_percent, "progress": disk_percent}
        ]

        for p in psutil.process_iter(['name', "cmdline"]):
            # 中台主入口
            if p.info['name'] == "java" and p.info['cmdline'][-1] in [
                "com.nubomed.mid.drug.DrugMiddlewareServer",
                "com.nubomed.mid.ecart.ECartServiceApp",
                "com.nubomed.mid.consumable.cabinet.ConsumableCabinetApp",
                "com.nubomed.autolabel.AutoLabelApp"
            ]:
                self.system_info_model.append({"name": self.tr("Middleware"), "status": self.tr("running"), "progress": 100})
            elif p.info['name'] == "java" and p.info['cmdline'][-1] == "com.nubomed.mid.cabinet.edge.CabinetEdgeApp":
                self.system_info_model.append({"name": self.tr("Smart Cart"), "status": self.tr("running"), "progress": 100})
            elif p.info["name"] == "mysqld":
                self.system_info_model.append({"name": self.tr("MySQL"), "status": self.tr("running"), "progress": 100})
            elif p.info["name"] == "ntpd":
                self.system_info_model.append({"name": self.tr("NTP"), "status": self.tr("running"), "progress": 100})

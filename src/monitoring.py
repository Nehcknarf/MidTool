import psutil

from PySide6.QtCore import QAbstractListModel, QByteArray, Qt, QModelIndex, Slot, QUrl
from PySide6.QtQml import QmlElement

from process import Process
from utils.adapter import product_type, consumable_cabinet_path, consumable_cabinet_cfg, ecart_cfg, ecart_path, \
    consumable_cabinet_service, ecart_service
from utils.log import logger


QML_IMPORT_NAME = "src.monitoring"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0


@QmlElement
class MiddlewareManager(Process):
    @Slot(str)
    def start_middleware(self, password):
        logger.info("Start middleware...")
        if product_type == 0:
            self.start(f"pm2 start {consumable_cabinet_path + consumable_cabinet_cfg} -m && pm2 save -m")
        elif product_type == 2:
            self.start(f"pm2 start {ecart_path + ecart_cfg} -m && pm2 save -m")
        elif product_type == 1:
            self.start(f"sudo supervisorctl start all", password=password)

    @Slot(str)
    def restart_middleware(self, password):
        logger.info("Restart middleware...")
        if product_type == 0:
            self.start(f"pm2 restart {consumable_cabinet_service} -m")
        elif product_type == 2:
            self.start(f"pm2 restart {ecart_service} -m")
        elif product_type == 1:
            self.start(f"sudo supervisorctl restart all", password=password)

    @Slot(str)
    def stop_middleware(self, password):
        logger.info("Stop middleware...")
        if product_type == 0:
            self.start(f"pm2 stop {consumable_cabinet_service} -m")
        elif product_type == 2:
            self.start(f"pm2 stop {ecart_service} -m")
        elif product_type == 1:
            self.start(f"sudo supervisorctl stop all", password=password)


@QmlElement
class SystemInfoModel(QAbstractListModel):
    NameRole = Qt.UserRole + 1
    StatusRole = Qt.UserRole + 2

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
        else:
            ret = None
        return ret

    def roleNames(self):
        default = super().roleNames()
        default[self.NameRole] = QByteArray(b"name")
        default[self.StatusRole] = QByteArray(b"status")
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
        disk_percent = psutil.disk_usage("/").percent

        status = self.tr("stopped")
        for p in psutil.process_iter(['name', "cmdline"]):
            # 中台主入口
            if p.info['name'] == "java":
                if p.info['cmdline'][-1] in ["com.nubomed.mid.drug.DrugMiddlewareServer", "com.nubomed.mid.ecart.ECartServiceApp", "com.nubomed.mid.consumable.cabinet.ConsumableCabinetApp"]:
                    # psutil返回被进程管理应用守护的中台状态不准确，running时始终为sleeping
                    # status = p.status()
                    status = self.tr("running")

        self.system_info_model = [
            {"name": self.tr("CPU"), "status": format(cpu_percent, ".1f")},
            {"name": self.tr("Memory"), "status": format(memory_percent, ".1f")},
            {"name": self.tr("Disk"), "status": format(disk_percent, ".1f")},
            {"name": self.tr("Middleware"), "status": status}
        ]

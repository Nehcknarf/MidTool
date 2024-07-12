from pathlib import Path

import psutil

from PySide6.QtCore import QAbstractListModel, QByteArray, Qt, QModelIndex, Slot
from PySide6.QtQml import QmlElement

from process import Process
from utils.adapter import product_type, consumable_cabinet_path, consumable_cabinet_cfg, ecart_cfg, ecart_path, \
    consumable_cabinet_service, ecart_service, consumable_cabinet_offline_path, consumable_cabinet_offline_cfg, \
    consumable_cabinet_offline_service, autolabel_path, autolabel_cfg, autolabel_service
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
            if Path(consumable_cabinet_offline_path).exists():
                self.start(f"pm2 start {consumable_cabinet_offline_cfg} -m && pm2 save -m", workdir=consumable_cabinet_offline_path, wait=True)
            self.start(f"pm2 start {consumable_cabinet_cfg} -m && pm2 save -m", workdir=consumable_cabinet_path)
        elif product_type == 1:
            self.start(f"sudo supervisorctl start all", password=password)
        elif product_type == 2:
            self.start(f"pm2 start {ecart_cfg} -m && pm2 save -m", workdir=ecart_path)
        elif product_type == 3:
            self.start(f"pm2 start {autolabel_cfg} -m && pm2 save -m", workdir=autolabel_path)

    @Slot(str)
    def restart_middleware(self, password):
        logger.info("Restart middleware...")
        if product_type == 0:
            if Path(consumable_cabinet_offline_path).exists():
                self.start(f"pm2 restart {consumable_cabinet_offline_service} -m", wait=True)
            self.start(f"pm2 restart {consumable_cabinet_service} -m")
        elif product_type == 1:
            self.start(f"sudo supervisorctl restart all", password=password)
        elif product_type == 2:
            self.start(f"pm2 restart {ecart_service} -m")
        elif product_type == 3:
            self.start(f"pm2 restart {autolabel_service} -m")

    @Slot(str)
    def stop_middleware(self, password):
        logger.info("Stop middleware...")
        if product_type == 0:
            if Path(consumable_cabinet_offline_path).exists():
                self.start(f"pm2 stop {consumable_cabinet_offline_service} -m", wait=True)
            self.start(f"pm2 stop {consumable_cabinet_service} -m")
        elif product_type == 1:
            self.start(f"sudo supervisorctl stop all", password=password)
        elif product_type == 2:
            self.start(f"pm2 stop {ecart_service} -m")
        elif product_type == 3:
            self.start(f"pm2 stop {autolabel_service} -m")


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
        # 中台状态
        status, progress = self.tr("stopped"), 0
        for p in psutil.process_iter(['name', "cmdline"]):
            # 中台主入口
            if p.info['name'] == "java" and p.info['cmdline'][-1] in [
                "com.nubomed.mid.drug.DrugMiddlewareServer",
                "com.nubomed.mid.ecart.ECartServiceApp",
                "com.nubomed.mid.consumable.cabinet.ConsumableCabinetApp",
                "com.nubomed.autolabel.AutoLabelApp"
            ]:
                status, progress = self.tr("running"), 100

        self.system_info_model = [
            {"name": self.tr("Middleware"), "status": status, "progress": progress},
            {"name": self.tr("CPU"), "status": cpu_percent, "progress": cpu_percent},
            {"name": self.tr("Memory"), "status": memory_percent, "progress": memory_percent},
            {"name": self.tr("Disk"), "status": disk_percent, "progress": disk_percent}
        ]

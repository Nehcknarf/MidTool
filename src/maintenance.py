import glob
from pathlib import Path

from PySide6.QtCore import Property, Signal, Slot, QUrl
from PySide6.QtQml import QmlElement

from process import Process
from utils.log import logger
from utils.adapter import root_path


QML_IMPORT_NAME = "src.maintenance"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0


@QmlElement
class Maintenance(Process):
    cabinetsChanged = Signal()
    backupChanged = Signal()

    def get_cabinets(self):
        p = Path("/nubomed/Device_defaultconf")
        if p.exists():
            return [x.name for x in p.iterdir() if x.is_dir()]
        else:
            return []

    cabinets = Property(list, get_cabinets, notify=cabinetsChanged)

    @Slot(str)
    def install_middleware(self, type):
        if wd := glob.glob("/nubomed/consumable-cabinet-service_V*/"):
            logger.info(f"Try to install middleware in {type}...")
            self.start(f"bash install.sh '{type}'", wd[0])
        else:
            logger.error(f"Middleware install package not found, install failed.")
            self.Stdout.emit(self.tr("Please confirm middleware install package has already unzip under "
                                     "\"/nubomed/consumable-cabinet-service_V*/\""))

    @Slot(QUrl)
    def update_middleware(self, qurl):
        update_pkg_path = qurl.toLocalFile()
        logger.info(f"Try to update middleware using {update_pkg_path}...")
        self.start(f"bash update.sh {update_pkg_path}", f"{root_path}/script/")

    def get_middleware_backup(self):
        p = Path("/nubomed/mid_bakup")
        if p.exists():
            return [f"{x.name[:4]}-{x.name[4:6]}-{x.name[6:8]} {x.name[8:10]}:{x.name[10:12]}:{x.name[12:14]}"
                    for x in p.iterdir() if x.is_dir()]
        else:
            logger.warning(f"There is no middleware backup.")

    backups = Property(list, get_middleware_backup, notify=backupChanged)

    @Slot(str)
    def restore_middleware(self, backup):
        logger.info(f"Try to restore middleware using {backup} backup...")
        self.start(f"bash restore.sh '{backup}'", f"{root_path}/script/")

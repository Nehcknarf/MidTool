# TODO 整合glob
import glob
from pathlib import Path

from PySide6.QtCore import Property, Signal, Slot, QUrl
from PySide6.QtQml import QmlElement

from process import Process
from src.utils.env import root_path


QML_IMPORT_NAME = "src.maintenance"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0


@QmlElement
class Maintenance(Process):
    cabinetsChanged = Signal()

    def get_cabinets(self):
        p = Path("/nubomed/Device_defaultconf")
        if p.exists():
            return [x.name for x in p.iterdir() if x.is_dir()]

    cabinets = Property(list, get_cabinets, notify=cabinetsChanged)

    @Slot(int)
    def install_middleware(self, type):
        if wd := glob.glob("/nubomed/consumable-cabinet-service_V*/"):
            self.start(f"bash install.sh {type}", wd[0])
        else:
            self.Stdout.emit(self.tr("Please confirm middleware install package has already unzip under "
                                     "\"/nubomed/consumable-cabinet-service_V*/\""))

    @Slot(QUrl)
    def update_middleware(self, qurl):
        update_pkg_path = qurl.toLocalFile()
        self.start(f"bash upgrade_version.sh {update_pkg_path}", f"{root_path}/script/")

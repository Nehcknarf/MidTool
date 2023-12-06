from PySide6.QtCore import Slot
from PySide6.QtQml import QmlElement

from process import Process
from utils.adapter import root_path
from utils.log import logger


QML_IMPORT_NAME = "src.network"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0


@QmlElement
class Network(Process):
    @Slot(str, str)
    def telnet(self, ip, port):
        self.start(f"echo \"\" | telnet {ip} {port}")

    @Slot()
    def show_route(self):
        # self.start("ip route show")
        self.start("route -n")

    @Slot(str, str, str, str)
    def add_route(self, destination, mask, gateway, password):
        logger.info(f"Try to add ip route {destination}/{mask} via {gateway}")
        self.start(f"sudo ip route add {destination}/{mask} via {gateway}", password=password)
        self.Stdout.emit(self.tr("Add ip route {}/{} via {}").format(destination, mask, gateway))

    @Slot(str, str, str)
    def del_route(self, destination, mask, password):
        logger.info(f"Try to del ip route {destination}/{mask}")
        self.start(f"sudo ip route del {destination}/{mask}", password=password)
        self.Stdout.emit(self.tr("Del ip route {}/{}").format(destination, mask))

    @Slot()
    def adj_priority(self):
        logger.info(f"Try to adjust ethernet priority")
        self.start(f"bash priority.sh", f"{root_path}/script/")

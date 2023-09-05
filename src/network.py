from PySide6.QtCore import Slot
from PySide6.QtQml import QmlElement

from process import Process


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
        self.start("ip route show")

    @Slot(str, str, str, str)
    def add_route(self, destination, mask, gateway, password):
        self.start(f"sudo ip route add {destination}/{mask} via {gateway}", password=password)

    @Slot(str, str, str)
    def del_route(self, destination, mask, password):
        self.start(f"sudo ip route del {destination}/{mask}", password=password)

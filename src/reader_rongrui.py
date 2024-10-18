import json

from PySide6.QtCore import Slot, QObject, Signal, Property
from PySide6.QtNetwork import QNetworkRequest, QNetworkAccessManager, QNetworkReply
from PySide6.QtQml import QmlElement
from PySide6.QtSerialPort import QSerialPortInfo

QML_IMPORT_NAME = "src.reader.rongrui"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0


@QmlElement
class ReaderRongRui(QObject):
    Response = Signal(str)
    getPort = Signal()
    getBaudRate = Signal()

    def __init__(self):
        super().__init__()
        self.manager = QNetworkAccessManager()
        self.manager.finished.connect(self.handle_response)
        self.base_url = "http://127.0.0.1:8087"
        self.handle = None

        self.ports = [port.portName() for port in QSerialPortInfo.availablePorts()]
        self.baud_rates = QSerialPortInfo.standardBaudRates()

    def get_ports(self):
        return self.ports

    def set_ports(self, ports):
        if self.ports != ports:
            self.ports = ports
            self.getPort.emit()

    @Slot()
    def update_ports(self):
        return [com.portName() for com in QSerialPortInfo.availablePorts()]

    availablePorts = Property(list, get_ports, set_ports, notify=getPort)

    def get_baud_rates(self):
        return self.baud_rates

    baudRates = Property(list, get_baud_rates, notify=getBaudRate)

    @Slot()
    def open(self):
        ip = "192.168.0.11"
        port = 6000
        request = QNetworkRequest(f"{self.base_url}/device/openNetPort?ipAddr={ip}&portNo={port}")
        self.manager.get(request)

    @Slot()
    def close(self):
        if self.handle is not None:
            request = QNetworkRequest(f"{self.base_url}/device/closeNetPort?frmHandle={self.handle}")
            self.manager.get(request)

    @Slot()
    def openRF(self):
        if self.handle is not None:
            request = QNetworkRequest(f"{self.base_url}/device/openRf?frmHandle={self.handle}")
            self.manager.get(request)

    @Slot()
    def closeRF(self):
        if self.handle is not None:
            request = QNetworkRequest(f"{self.base_url}/device/closeRf?frmHandle={self.handle}")
            self.manager.get(request)

    @Slot(str, int)
    def openSerialPort(self, port, baudrate):
        if self.handle is not None:
            request = QNetworkRequest(f"{self.base_url}/device/openByCom?serialPoint=/dev/{port}&speed={baudrate}")
            self.manager.get(request)

    @Slot()
    def closeSerialPort(self):
        if self.handle is not None:
            request = QNetworkRequest(f"{self.base_url}/device/closeByCom?frmHandle={self.handle}")
            self.manager.get(request)

    @Slot()
    def checkInventory(self):
        if self.handle is not None:
            request = QNetworkRequest(f"{self.base_url}/device/inventory?frmHandle={self.handle}")
            self.manager.get(request)

    @Slot(QNetworkReply)
    def handle_response(self, reply: QNetworkReply):
        if reply.error() == QNetworkReply.NoError:
            raw = reply.readAll().data().decode()
            response = json.loads(raw)
            print(response)
            if response.get("frmHandle"):
                self.handle = response.get("frmHandle")
            elif response.get("result"):
                self.Response.emit(response.get("result"))
            elif response.get("allTagNum"):
                self.Response.emit(self.tr(f'There are {response.get("allTagNum")} tags in inventory.'))
        reply.deleteLater()

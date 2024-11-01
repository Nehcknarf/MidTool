import json
from datetime import datetime

from PySide6.QtCore import Slot, QUrl, QObject, Signal, Property
from PySide6.QtQml import QmlElement
from PySide6.QtNetwork import QNetworkRequest, QNetworkAccessManager, QNetworkReply
from PySide6.QtSerialPort import QSerialPortInfo

from process import Process
from utils.log import logger
from utils.adapter import root_path

QML_IMPORT_NAME = "src.reader"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0


@QmlElement
class Reader(Process):
    @Slot()
    def start_config(self):
        logger.info(f"Try to config RFID reader...")
        self.start(f"bash start.sh", f"{root_path}/script/RFIDReader/")

    @Slot(QUrl, str)
    def record(self, qurl, text):
        save_dir = qurl.toLocalFile()
        with open(f"{save_dir}/reader_records.txt", "w") as f:
            f.write(text)


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
        self.ports = [com.portName() for com in QSerialPortInfo.availablePorts()]

    availablePorts = Property(list, get_ports, set_ports, notify=getPort)

    def get_baud_rates(self):
        return self.baud_rates

    baudRates = Property(list, get_baud_rates, notify=getBaudRate)

    @Slot(str, int)
    def open(self, port, baudrate):
        request = QNetworkRequest(f"{self.base_url}/device/openByCom?serialPoint=/dev/{port}&speed={baudrate}")
        self.manager.get(request)

    @Slot()
    def close(self):
        if self.handle is not None:
            request = QNetworkRequest(f"{self.base_url}/device/closeRf?frmHandle={self.handle}")
            self.manager.get(request)
            self.handle = None

    @Slot()
    def checkInventory(self):
        if self.handle is not None:
            request = QNetworkRequest(f"{self.base_url}/device/inventory?frmHandle={self.handle}")
            self.manager.get(request)
            self.Response.emit("请等待接口返回盘点结果... 过程耗时约2~3s，按钮有3s冷却时间，期间重复点击无效")

    @Slot(QNetworkReply)
    def handle_response(self, reply: QNetworkReply):
        if reply.error() == QNetworkReply.NoError:
            raw = reply.readAll().data().decode()
            response = json.loads(raw)
            # print(response)
            # 收到包含句柄的响应则发送打开天线请求
            if response.get("frmHandle"):
                self.handle = response.get("frmHandle")
                request = QNetworkRequest(f"{self.base_url}/device/openRf?frmHandle={self.handle}")
                self.manager.get(request)
            elif result := response.get("result"):
                self.Response.emit(result)
                # 收到关闭天线成功的响应则发送关闭读写器请求
                if result == "关闭感应射频场成功" and self.handle is not None:
                    request = QNetworkRequest(f"{self.base_url}/device/closeByCom?frmHandle={self.handle}")
                    self.manager.get(request)
            elif count := response.get("allTagNum"):
                self.Response.emit(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')}，共计有 {count} 个标签")
        reply.deleteLater()

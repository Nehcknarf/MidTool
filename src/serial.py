import re
import struct
from datetime import datetime

from PySide6.QtCore import QObject, Slot, Signal, Property, QIODevice, QCoreApplication
from PySide6.QtQml import QmlElement
from PySide6.QtSerialPort import QSerialPort, QSerialPortInfo

from utils.log import logger


QML_IMPORT_NAME = "src.serial"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0


@QmlElement
class Serial(QObject):
    comChanged = Signal()
    Pinout = Signal(str)

    def __init__(self):
        super().__init__()
        self.ser = QSerialPort()
        self.ser.readyRead.connect(self.read)
        self.total_data = b''
        # 串口设备类型
        self.device_dict = {
            "0708": self.tr("RFID reader"),
            "0107": self.tr("Code scanner"),
            "020a": self.tr("Human presence sensor")
        }

    def get_ports(self):
        return [com.portName() for com in QSerialPortInfo.availablePorts()]

    def get_baud_rates(self):
        return QSerialPortInfo.standardBaudRates()

    coms = Property(list, get_ports, notify=comChanged)
    baud_rates = Property(list, get_baud_rates, notify=comChanged)

    @Slot(str, int)
    def open_device(self, port_name, baud_rate):
        if self.ser.isOpen():
            return
        else:
            logger.info(f"Try to connect serial port through {port_name}@{baud_rate}")
            self.ser.setPortName(port_name)
            self.ser.setBaudRate(int(baud_rate))
            # self.ser.setReadBufferSize(0)
            if self.ser.open(QIODevice.ReadOnly):
                self.Pinout.emit(self.tr("Serial port is opening"))
            else:
                self.Pinout.emit(self.tr("Serial port open failed"))

    @Slot()
    def close_device(self):
        if self.ser.isOpen():
            self.ser.close()
            self.Pinout.emit(self.tr("Serial port is closed"))

    @Slot()
    def read(self):
        if self.ser.bytesAvailable():
            bytes_data = self.ser.readAll().data()  # bytes
            self.total_data += bytes_data
            logger.info(f"Serial port pinout: {self.total_data}")
            # self.Pinout.emit(self.tr("Data flow: {}, String: {}").format(self.total_data.hex(), str(self.total_data)))
            if length_domain := re.findall(b'~(.{2})\x02', self.total_data):
                try:
                    length = struct.unpack("h", length_domain[0])[0] + 4  # 版本号到数据域的长度 + 长度域 + 校验域 = 总长度
                except struct.error as err:
                    self.Pinout.emit(self.tr("Length field parse failed, {}").format(err))
                else:
                    if pack_data := re.findall(b'~.{' + f'{length}'.encode() + b'}\xe7', self.total_data, re.DOTALL):
                        pack_data = pack_data[0]
                        try:
                            header_tuple = struct.unpack("<chc4s4s2h2scB2s2ch", pack_data[:26])  # 起始域到参数长度域
                        except struct.error as err:
                            self.Pinout.emit(self.tr("Header parse failed, {}").format(err))
                        else:
                            header_list = [i.hex() if isinstance(i, bytes) else i for i in header_tuple]
                            device_type = header_list[10]  # 单元类型
                            payload_length = header_list[-1]  # 参数长度
                            # self.total_data = self.total_data[29 + payload_length + 3:]
                            self.total_data = b''
    
                            if device_type == "0708":
                                try:
                                    payload_tuple = struct.unpack(f"{payload_length}B", pack_data[26:26 + payload_length])
                                except struct.error as err:
                                    sig_data = self.tr("Data load parse failed, {}").format(err)
                                else:
                                    # 自动上报RFID号
                                    card_type = payload_tuple[0]
                                    card_uid = "-".join(map(str, payload_tuple[1:]))
                                    sig_data = self.tr("Device type: {}, Card type: {}, Card number: {}").format(self.device_dict.get(device_type), card_type, card_uid)
                            elif device_type == "0107":
                                try:
                                    payload_tuple = struct.unpack(f"{payload_length}B", pack_data[26:26 + payload_length])
                                    # ending_tuple = struct.unpack("2sc", pack_data[26 + payload_length:29 + payload_length])
                                except struct.error as err:
                                    sig_data = self.tr("Data load parse failed, {}").format(err)
                                else:
                                    # ending_list = [i.hex() for i in ending_tuple]
                                    # unpack_data = tuple(header_list) + payload_tuple + tuple(ending_list)
                                    # print(unpack_data)
                                    # 自动上报扫描码内容
                                    code_content = "".join(map(str, payload_tuple[2:]))
                                    sig_data = self.tr("Device type: {}, Barcode content: {}").format(self.device_dict.get(device_type), code_content)
                            elif device_type == "020a":
                                try:
                                    payload_tuple = struct.unpack(f"{payload_length}B", pack_data[26:26 + payload_length])
                                except struct.error as err:
                                    sig_data = self.tr("Data load parse failed, {}").format(err)
                                else:
                                    # 自动上报人位置状态变化
                                    state_dict = {
                                        1: self.tr("Human is within the area"),
                                        0: self.tr("Human left the area")
                                    }
                                    sig_data = self.tr("Device type: {}, {}").format(self.device_dict.get(device_type), state_dict.get(payload_tuple[0]))
                            else:
                                sig_data = self.tr("Device type is not yet supported for parsing")
                            self.Pinout.emit(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')}，{sig_data}")
                    else:
                        pass
            else:
                self.total_data = b''

import re
import struct
from datetime import datetime

from PySide6.QtCore import QObject, QRunnable, QCoreApplication, Slot
from PySide6.QtQml import QmlElement
from PySide6.QtSerialPort import QSerialPort


class Reader(QRunnable):
    def __init__(self, signal, ser):
        super().__init__()
        self.signal = signal
        self.ser = ser
        self.total_data = b''

    @Slot()
    def run(self):
        device_dict = {
            "0708": QCoreApplication.translate("Serial", "身份RFID读卡器类"),
            "0107": QCoreApplication.translate("Serial", "条码扫描头类"),
            "020a": QCoreApplication.translate("Serial", "人体感应类")
        }
        bytes_data = self.ser.readAll().data()  # bytes
        self.total_data += bytes_data
        self.signal.emit(QCoreApplication.translate("Serial", "数据流：{}，字符串：{}").format(self.total_data.hex(), str(self.total_data)))
        if length_domain := re.findall(b'~(.{2})\x02', self.total_data):
            try:
                length = struct.unpack("h", length_domain[0])[0] + 4  # 版本号到数据域的长度 + 长度域 + 校验域 = 总长度
            except struct.error as err:
                self.signal.emit(QCoreApplication.translate("Serial", "长度域解析失败，{}").format(err))
            else:
                if pack_data := re.findall(b'~.{'+f'{length}'.encode()+b'}\xe7', self.total_data, re.DOTALL):
                    pack_data = pack_data[0]
                    # self.signal.emit(QCoreApplication.translate("Serial", "接收到的原始数据包：{}").format(pack_data.hex()))
                    try:
                        header_tuple = struct.unpack("<chc4s4s2h2scB2s2ch", pack_data[:26])  # 起始域到参数长度域
                    except struct.error as err:
                        self.signal.emit(QCoreApplication.translate("Serial", "数据头解析失败，{}").format(err))
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
                                sig_data = QCoreApplication.translate("Serial", "数据载荷解析失败，{}").format(err)
                            else:
                                # 自动上报RFID号
                                card_type = payload_tuple[0]
                                card_uid = "-".join(map(str, payload_tuple[1:]))
                                sig_data = QCoreApplication.translate("Serial", "设备类型：{}，卡类型：{}，卡号：{}").format(device_dict.get(device_type), card_type, card_uid)
                        elif device_type == "0107":
                            try:
                                payload_tuple = struct.unpack(f"{payload_length}B", pack_data[26:26 + payload_length])
                                # ending_tuple = struct.unpack("2sc", pack_data[26 + payload_length:29 + payload_length])
                            except struct.error as err:
                                sig_data = QCoreApplication.translate("Serial", "数据载荷解析失败，{}").format(err)
                            else:
                                # ending_list = [i.hex() for i in ending_tuple]
                                # unpack_data = tuple(header_list) + payload_tuple + tuple(ending_list)
                                # print(unpack_data)
                                # 自动上报扫描码内容
                                code_content = "".join(map(str, payload_tuple[2:]))
                                sig_data = QCoreApplication.translate("Serial", "设备类型：{}，条码内容：{}").format(device_dict.get(device_type), code_content)
                        elif device_type == "020a":
                            try:
                                payload_tuple = struct.unpack(f"{payload_length}B", pack_data[26:26 + payload_length])
                            except struct.error as err:
                                sig_data = QCoreApplication.translate("Serial", "数据载荷解析失败，{}").format(err)
                            else:
                                # 自动上报人位置状态变化
                                state_dict = {
                                    1: QCoreApplication.translate("Serial", "人在指定范围内"),
                                    0: QCoreApplication.translate("Serial", "人离开了指定范围")
                                }
                                sig_data = QCoreApplication.translate("Serial", "设备类型：{}，{}").format(device_dict.get(device_type), state_dict.get(payload_tuple[0]))
                        else:
                            sig_data = QCoreApplication.translate("Serial", "尚未支持解析的设备类型")
                        self.signal.emit(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')}，{sig_data}")
                else:
                    pass
                    # self.signal.emit(QCoreApplication.translate("Serial", "未匹配到数据包"))
        else:
            self.total_data = b''
            # self.signal.emit(QCoreApplication.translate("Serial", "未找到特征（长度域）"))


@QmlElement
class Serial(QObject):
    def __init__(self):
        super().__init__()
        self.ser = QSerialPort()
        self.ser.readyRead.connect(self.read)

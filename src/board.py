import socket
import struct

from PySide6.QtCore import Qt, QObject, Signal, Slot, QAbstractTableModel
from PySide6.QtNetwork import QUdpSocket, QHostAddress
from PySide6.QtQml import QmlElement

from utils.log import logger

QML_IMPORT_NAME = "src.board"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0


class UdpHandler(QObject):
    dataChanged = Signal()
    board_dict = dict()

    def __init__(self):
        super().__init__()
        self.socket = QUdpSocket()
        self.socket.readyRead.connect(self.read_datagrams)

    def read_datagrams(self):
        while self.socket.hasPendingDatagrams():
            data, host, port = self.socket.readDatagram(self.socket.pendingDatagramSize())
            pack_data = data.data()
            if len(pack_data) == 36:  # 搜索指令的返回结果（36字节)
                ip = socket.inet_ntoa(pack_data[5:9])
                mac = pack_data[9:15].hex().upper()
                firmware_ver = struct.unpack('<H', pack_data[15:17])[0]
                device_name = pack_data[19:35].rstrip(b'\x00').decode('ascii')
                UdpHandler.board_dict.update(
                    {ip: [ip, device_name, mac, firmware_ver, None, None, None, None, None, None, None]})
                self.read_cfg(mac)
            elif len(pack_data) == 130:
                dhcp = pack_data[3] & 0x80
                ip = socket.inet_ntoa(pack_data[9:13][::-1])
                gateway = socket.inet_ntoa(pack_data[13:17][::-1])
                mask = socket.inet_ntoa(pack_data[17:21][::-1])
                target_port = struct.unpack('<H', pack_data[81:83])[0]
                target_ip = pack_data[83:113].rstrip(b'\x00').decode('ascii')
                UdpHandler.board_dict[ip][4:9] = [gateway, mask, dhcp, target_ip, target_port]
                UdpHandler.board_dict[ip][9] = pack_data[:67]  # 基础参数
                UdpHandler.board_dict[ip][10] = pack_data[67:]  # 串口0参数
            else:
                print("Return:", pack_data)
            self.dataChanged.emit()

    @staticmethod
    def calc_checksum(string):
        checksum = 0
        # 遍历字符串的每个字符，计算其十六进制值的和
        for i in range(2, len(string), 2):
            byte = string[i:i + 2]
            checksum += int(byte, 16)
        # 只保留低字节 (0xFF)
        checksum &= 0xFF
        return hex(checksum).replace("0x", "").zfill(2).upper()

    def discover(self):
        logger.info("Discovering Boards...")
        message = bytes.fromhex("FF010102")
        self.socket.writeDatagram(message, QHostAddress.Broadcast, 1901)

    def command(self, mac, length, cmd, arg=""):
        string = f"FF{length}{cmd}{mac}61646D696E0061646D696E00{arg}"
        string += self.calc_checksum(string)
        # print(string)
        message = bytes.fromhex(string)
        self.socket.writeDatagram(message, QHostAddress.Broadcast, 1901)

    def reboot(self, mac):
        print("Reboot device...")
        self.command(mac, length=13, cmd="02")

    def read_cfg(self, mac):
        print("Retrieving device info...")
        self.command(mac, length=13, cmd="03")

    def save_cfg(self, mac):
        print("Saving...")
        self.command(mac, length=13, cmd="04")

    def cfg_basic(self, board_info, dhcp=128):
        ip = board_info[0]
        mac = board_info[2]
        gateway = board_info[4]
        mask = board_info[5]
        raw_basic = bytearray(board_info[9])
        if dhcp == 0:  # DHCP
            board_info[6] = 0
            raw_basic[3] = 0
        elif dhcp == 128:  # 静态
            board_info[6] = 128
            raw_basic[3] = 128
        raw_basic[9:13] = socket.inet_aton(ip)[::-1]
        raw_basic[13:17] = socket.inet_aton(gateway)[::-1]
        raw_basic[17:21] = socket.inet_aton(mask)[::-1]
        board_info[9] = bytes(raw_basic)
        arg = board_info[9].hex().upper()
        self.command(mac, length=56, cmd="05", arg=arg)
        self.save_cfg(mac)

    def cfg_serial(self, board_info):
        mac = board_info[2]
        target_ip = board_info[7]
        target_port = int(board_info[8])
        raw_serial = bytearray(board_info[10])
        raw_serial[14:16] = struct.pack('<H', target_port)
        raw_serial[16:46] = target_ip.encode('ascii').ljust(30, b'\x00')
        board_info[10] = bytes(raw_serial)
        arg = board_info[10].hex().upper()
        self.command(mac, length=52, cmd="06", arg=arg)
        self.save_cfg(mac)


@QmlElement
class TableModel(QAbstractTableModel):
    HyperLinkRole = Qt.UserRole + 1
    EmbButtonRole = Qt.UserRole + 2

    def __init__(self, parent=None):
        super().__init__(parent)
        self.udp_handler = UdpHandler()
        self.udp_handler.dataChanged.connect(self.refresh)

    @Slot()
    def refresh(self):
        self.beginResetModel()
        self.endResetModel()

    @Slot()
    def discover(self):
        self.beginResetModel()
        UdpHandler.board_dict.clear()
        self.udp_handler.discover()
        self.endResetModel()

    @Slot(str)
    def reboot(self, mac):
        self.udp_handler.reboot(mac)

    @Slot(list, int)
    def setDhcp(self, board_info, dhcp):
        self.udp_handler.cfg_basic(board_info, dhcp)

    def roleNames(self):
        roles = super().roleNames()
        roles[TableModel.HyperLinkRole] = b'hyperlink'
        roles[TableModel.EmbButtonRole] = b'embbutton'
        return roles

    def rowCount(self, parent=None):
        return len(UdpHandler.board_dict)

    def columnCount(self, parent=None):
        return 11

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal:
            return \
                [self.tr("IP"), self.tr("Home Page"), self.tr("Name"), self.tr("MAC"), self.tr("Version"),
                 self.tr("Gateway"), self.tr("Mask"), self.tr("IP Type"), self.tr("Target IP"), self.tr("Target Port"),
                 self.tr("Reboot")][section]

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            row = index.row()
            column = index.column()

            board_info = list(UdpHandler.board_dict.values())[row]
            ip = board_info[0]
            name = board_info[1]
            mac = board_info[2]
            firmware_ver = board_info[3]
            gateway = board_info[4]
            mask = board_info[5]
            # dhcp = board_info[6]
            target_ip = board_info[7]
            target_port = board_info[8]

            if role == Qt.DisplayRole:
                match column:
                    case 0:
                        return ip
                    case 2:
                        return name
                    case 3:
                        return mac
                    case 4:
                        return firmware_ver
                    case 5:
                        return gateway
                    case 6:
                        return mask
                    case 7:  # DHCP
                        return board_info
                    case 8:
                        return target_ip
                    case 9:
                        return target_port
            elif role == TableModel.EmbButtonRole:
                match column:
                    case 10:
                        return mac
            elif role == TableModel.HyperLinkRole:
                match column:
                    case 1:
                        return ip

    def setData(self, index, value, role=...):
        row = index.row()
        column = index.column()
        board_info = list(UdpHandler.board_dict.values())[row]
        if role == Qt.DisplayRole:
            match column:
                case 0:
                    board_info[0] = value
                    self.udp_handler.cfg_basic(board_info)
                case 5:
                    board_info[4] = value
                    self.udp_handler.cfg_basic(board_info)
                case 6:
                    board_info[5] = value
                    self.udp_handler.cfg_basic(board_info)
                case 7:  # DHCP
                    pass
                case 8:
                    board_info[7] = value
                    self.udp_handler.cfg_serial(board_info)
                case 9:
                    board_info[8] = value
                    self.udp_handler.cfg_serial(board_info)
            self.dataChanged.emit(index, index)
            return True
        return False

    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable

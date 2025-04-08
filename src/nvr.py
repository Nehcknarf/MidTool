import uuid
import socket
import time
from datetime import datetime
# import xml.etree.ElementTree as ET
from lxml import etree as ET
import httpx

from PySide6.QtQml import QmlElement
from PySide6.QtCore import QObject, Signal, Slot, QThreadPool, QRunnable, QAbstractTableModel, Qt, QCoreApplication
from PySide6.QtNetwork import QHostAddress, QUdpSocket

from utils.log import logger
from utils.adapter import nvr_username, nvr_password, nvr_ip, ipc_ip
from utils.decrypt_util import AESUtil, PswUtil

QML_IMPORT_NAME = "src.nvr"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0

threadpool = QThreadPool()


class HikUdpHandler(QObject):
    """HIK 代表海康"""
    dataChanged = Signal()
    device_dict = dict()

    def __init__(self):
        super().__init__()
        ipv4 = self.get_host_ip()
        self.socket = QUdpSocket()
        self.socket.bind(QHostAddress(ipv4), 37020)
        self.socket.readyRead.connect(self.read_datagrams)

    @staticmethod
    def get_host_ip():
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(('192.168.0.1', 80))
            ipv4 = s.getsockname()[0]
        return ipv4

    def discover(self):
        print("Discovering NVR/IPC devices...")
        uuid_str = str(uuid.uuid4())
        message = f'<?xml version="1.0" encoding="utf-8"?><Probe><Uuid>"{uuid_str}"</Uuid><Types>inquiry</Types></Probe>'.encode('utf-8')
        self.socket.writeDatagram(message, QHostAddress("239.255.255.250"), 37020)

    def read_datagrams(self):
        while self.socket.hasPendingDatagrams():
            data, host, port = self.socket.readDatagram(self.socket.pendingDatagramSize())
            message = data.data()
            root = ET.fromstring(message)
            mac = root.find('MAC').text
            ip = root.find('IPv4Address').text
            mask = root.find('IPv4SubnetMask').text
            gateway = root.find('IPv4Gateway').text
            device_description = root.find('DeviceDescription').text
            software_version = root.find('SoftwareVersion').text
            print(f"IPv4: {ip}, Device Description: {device_description}")
            if "IPC" in device_description:
                HikUdpHandler.device_dict.update({mac: [mac, "IPC", ip, mask, gateway, device_description, software_version]})
            else:
                HikUdpHandler.device_dict.update({mac: [mac, "NVR", ip, mask, gateway, device_description, software_version]})
            self.dataChanged.emit()


@QmlElement
class HikTableModel(QAbstractTableModel):
    HyperLinkRole = Qt.UserRole + 1

    def __init__(self, parent=None):
        super().__init__(parent)
        self.udp_handler = HikUdpHandler()
        self.udp_handler.dataChanged.connect(self.refresh)

    @Slot()
    def refresh(self):
        self.beginResetModel()
        self.endResetModel()

    @Slot()
    def discover(self):
        self.beginResetModel()
        HikUdpHandler.device_dict.clear()
        self.udp_handler.discover()
        self.endResetModel()

    def roleNames(self):
        roles = super().roleNames()
        roles[HikTableModel.HyperLinkRole] = b'hyperlink'
        return roles

    def rowCount(self, parent=None):
        return len(HikUdpHandler.device_dict)

    def columnCount(self, parent=None):
        return 7

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal:
            return [self.tr("MAC"), self.tr("Type"), self.tr("IP"), self.tr("Mask"), self.tr("Gateway"), self.tr("Description"), self.tr("Version")][section]

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            row = index.row()
            column = index.column()
            device_info = list(HikUdpHandler.device_dict.values())[row]
            mac = device_info[0]
            device_type = device_info[1]
            ip = device_info[2]
            mask = device_info[3]
            gateway = device_info[4]
            device_description = device_info[5]
            software_version = device_info[6]

            if role == Qt.DisplayRole:
                match column:
                    case 0:
                        return mac
                    case 1:
                        return device_type
                    case 3:
                        return mask
                    case 4:
                        return gateway
                    case 5:
                        return device_description
                    case 6:
                        return software_version
            elif role == HikTableModel.HyperLinkRole:
                match column:
                    case 2:
                        return ip


class BaseHttpHandler:
    def __init__(self, ip):
        self.ip = ip
        self.session_id = ""
        self.session_tag = ""
        self.cookie = ""
        self.aes_key = ""
        self.xmlns = "{http://www.hikvision.com/ver20/XMLSchema}"

    def request(self, method, url, content=None):
        print(method, url)
        if self.session_id:
            headers = {'Cookie': f'WebSession={self.session_id}'}
        elif self.session_tag:
            headers = {'Cookie': f'{self.cookie}', 'Sessiontag': self.session_tag}
        else:
            headers = {'Cookie': f'{self.cookie}'}
        print(headers)
        match method:
            case "GET":
                try:
                    r = httpx.get(url, headers=headers).raise_for_status()
                except httpx.HTTPError as exc:
                    print(f"Error response {exc.response.status_code} while requesting {exc.request.url!r}.")
                else:
                    print(r.text)
                    return r.content
            case "POST":
                try:
                    r = httpx.post(url, headers=headers, content=content).raise_for_status()
                except httpx.HTTPError as exc:
                    print(f"Error response {exc.response.status_code} while requesting {exc.request.url!r}.")
                else:
                    if 'Set-Cookie' in r.headers:
                        self.cookie = r.headers['Set-Cookie'].split(';')[0]
                    print(r.text)
                    return r.content
            case "PUT":
                try:
                    xml_str = httpx.put(url, headers=headers, content=content, timeout=30).raise_for_status().text
                except httpx.HTTPError as exc:
                    print(f"Error response {exc.response.status_code} while requesting {exc.request.url!r}.")
                else:
                    print(xml_str)
                    return xml_str
            case "DELETE":
                try:
                    xml_str = httpx.delete(url, headers=headers).raise_for_status().text
                except httpx.HTTPError as exc:
                    print(f"Error response {exc.response.status_code} while requesting {exc.request.url!r}.")
                else:
                    print(xml_str)
                    return xml_str

    @staticmethod
    def get_timezone_format():
        local_tz = datetime.now().astimezone().tzinfo
        # 获取时区名称和UTC偏移
        offset = local_tz.utcoffset(None)
        # 将时差转换为小时
        hours = int(abs(offset.total_seconds()) // 3600)
        # 确定符号
        sign = '-' if offset.total_seconds() > 0 else ' '
        return f"CST{sign}{hours:02d}:00:00"

    def set_time(self):
        url = f"http://{self.ip}/ISAPI/System/time"
        xml = f"""
            <?xml version="1.0" encoding="utf-8"?>
            <Time>
                <timeMode>manual</timeMode>
                <localTime>{datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}</localTime>
                <timeZone>{self.get_timezone_format()}</timeZone>
            </Time>
            """
        self.request(method="PUT", url=url, content=xml)


class NvrHttpHandler(BaseHttpHandler):
    def __init__(self, ip):
        super().__init__(ip)

    def login(self, username=nvr_username, password=nvr_password):
        xml_str = self.request(method="GET", url=f"http://:{password}@{self.ip}/ISAPI/Security/sessionLogin/capabilities?username={username}")
        root = ET.fromstring(xml_str)
        session_id = root.find(f"{self.xmlns}sessionID").text  # 临时 token
        salt = root.find(f"{self.xmlns}salt").text
        challenge = root.find(f"{self.xmlns}challenge").text
        iterations = int(root.find(f"{self.xmlns}iterations").text)
        # 计算加密密码
        encode_pwd = PswUtil.encode_pwd(username, password, salt, challenge, iterations)
        self.aes_key = PswUtil.get_aes_key(password, username, salt, iterations)
        # 登录请求
        login_xml = f"""
        <SessionLogin>
            <userName>{username}</userName>
            <password>{encode_pwd}</password>
            <sessionID>{session_id}</sessionID>
        </SessionLogin>
        """
        xml_str = self.request(method="POST", url=f"http://{self.ip}/ISAPI/Security/sessionLogin?timeStamp={int(time.time() * 1000)}", content=login_xml)
        root = ET.fromstring(xml_str)
        if root.find(f"{self.xmlns}sessionID") is not None:
            self.session_id = root.find(f"{self.xmlns}sessionID").text  # 真 token

    def get_ipc_num(self):
        iv = PswUtil.get_iv()
        url = f"http://{self.ip}/ISAPI/ContentMgmt/InputProxy/channels?security=1&iv={iv}"
        xml_str = self.request(method="GET", url=url)
        root = ET.fromstring(xml_str)
        id_list = root.findall(f".//{self.xmlns}id")
        return [id.text for id in id_list]

    def del_ipc(self, index):
        url = f"http://{self.ip}/ISAPI/ContentMgmt/InputProxy/channels/{index}"
        self.request(method="DELETE", url=url)

    def add_ipc(self, ipc_ip, ipc_username=nvr_username, ipc_psw=nvr_password):
        iv = PswUtil.get_iv()
        ipc_username = PswUtil.get_n(ipc_username)
        ipc_username = AESUtil.encode_aes(ipc_username, self.aes_key, iv)
        ipc_psw = PswUtil.get_n(ipc_psw)
        ipc_psw = AESUtil.encode_aes(ipc_psw, self.aes_key, iv)

        xml = f"""
        <?xml version="1.0" encoding="utf-8"?>
        <InputProxyChannel>
            <id>0</id>
            <quickAdd>false</quickAdd>
            <sourceInputPortDescriptor>
                <proxyProtocol>HIKVISION</proxyProtocol>
                <addressingFormatType>ipaddress</addressingFormatType>
                <ipAddress>{ipc_ip}</ipAddress>
                <managePortNo>8000</managePortNo>
                <srcInputPort>1</srcInputPort>
                <userName>{ipc_username}</userName>
                <password>{ipc_psw}</password>
                <streamType>auto</streamType>
            </sourceInputPortDescriptor>
        </InputProxyChannel>"""

        self.request(method="POST", url=f"http://{self.ip}/ISAPI/ContentMgmt/InputProxy/channels?security=1&iv={iv}", content=xml)

    def set_encode(self, index=1):
        url = f"http://{self.ip}/ISAPI/ContentMgmt/StreamingProxy/channels/{index}01"
        xml = f"""
        <?xml version="1.0" encoding="UTF-8"?>
        <StreamingChannel xmlns="http://www.hikvision.com/ver20/XMLSchema" version="1.0">
            <id>{index}01</id>
            <channelName>{index}01</channelName>
            <enabled>true</enabled>
            <Transport>
                <ControlProtocolList>
                    <ControlProtocol>
                        <streamingTransport>RTSP</streamingTransport>
                    </ControlProtocol>
                </ControlProtocolList>
            </Transport>
            <Audio>
                <enabled>true</enabled>
                <audioInputChannelID>{index}</audioInputChannelID>
                <audioCompressionType>G.711alaw</audioCompressionType>
            </Audio>
            <Video xmlns="">
                <enabled>true</enabled>
                <dynVideoInputChannelID>{index}</dynVideoInputChannelID>
                <videoCodecType>H.264</videoCodecType>
                <videoResolutionWidth>1920</videoResolutionWidth>
                <videoScanType>progressive</videoScanType>
                <videoResolutionHeight>1080</videoResolutionHeight>
                <videoQualityControlType>cbr</videoQualityControlType>
                <constantBitRate>1024</constantBitRate>
                <maxFrameRate>2500</maxFrameRate>
            </Video>
        </StreamingChannel>
        """
        self.request(method="PUT", url=url, content=xml)

    def format(self):
        url = f"http://{self.ip}/ISAPI/ContentMgmt/Storage/hdd/1/format"
        self.request(method="PUT", url=url)

    def config_event(self, index=1):
        url = f"http://{self.ip}/ISAPI/ContentMgmt/InputProxy/channels/{index}/video/motionDetection"
        xml = """
        <?xml version="1.0" encoding="UTF-8"?>
        <MotionDetection xmlns="http://www.hikvision.com/ver20/XMLSchema" version="1.0">
            <enabled>false</enabled>
            <enableHighlight>false</enableHighlight>
            <samplingInterval>5</samplingInterval>
            <startTriggerTime>1000</startTriggerTime>
            <endTriggerTime>1000</endTriggerTime>
            <regionType>grid</regionType>
            <Grid>
                <rowGranularity>18</rowGranularity>
                <columnGranularity>22</columnGranularity>
            </Grid>
            <MotionDetectionLayout xmlns="http://www.hikvision.com/ver20/XMLSchema" version="1.0">
                <sensitivityLevel>60</sensitivityLevel>
                <layout>
                    <gridMap></gridMap>
                </layout>
            </MotionDetectionLayout>
        </MotionDetection>
        """
        self.request(method="PUT", url=url, content=xml)

    def close_record_scheduler(self, index=1):
        url = f"http://{self.ip}/ISAPI/ContentMgmt/record/tracks"
        xml = f"""
        <?xml version="1.0" encoding="UTF-8"?>
        <TrackList xmlns="http://www.hikvision.com/ver20/XMLSchema" version="1.0">
            <Track xmlns="http://www.hikvision.com/ver20/XMLSchema" version="1.0">
                <id>{index}01</id>
                <Channel>{index}01</Channel>
                <Enable>false</Enable>
                <Description>trackType=standard,contentType=video,codecType=H.264-BP,resolution=1920x1080,framerate=25.0 fps,bitrate=1024 kbps</Description>
                <TrackGUID>{00000000-0000-0000-0000-000000000000}</TrackGUID>
                <Size>1</Size>
                <Duration min="0" max="750">P0DT0H</Duration>
                <DefaultRecordingMode>CMR</DefaultRecordingMode>
                <SrcDescriptor>
                    <SrcGUID>{00000000-0000-0000-0000-000000000000}</SrcGUID>
                    <SrcChannel>{index}</SrcChannel>
                    <StreamHint/>
                    <SrcDriver/>
                    <SrcType/>
                    <SrcUrl>rtsp://localhost/PSIA/Streaming/channels/101</SrcUrl>
                    <SrcUrlMethods/>
                    <SrcLogin/>
                </SrcDescriptor>
                <TrackSchedule xmlns="">
                    <ScheduleBlockList>
                        <ScheduleBlock>
                            <ScheduleBlockGUID>{00000000-0000-0000-0000-000000000000}</ScheduleBlockGUID>
                            <ScheduleBlockType>www.std-cgi.com/racm/schedule/ver10</ScheduleBlockType>
                        </ScheduleBlock>
                    </ScheduleBlockList>
                </TrackSchedule>
                <CustomExtensionList>
                    <CustomExtension>
                        <CustomExtensionName>www.hikvision.com/RaCM/trackExt/ver10</CustomExtensionName>
                        <enableSchedule>false</enableSchedule>
                        <SaveAudio>true</SaveAudio>
                        <PreRecordTimeSeconds>5</PreRecordTimeSeconds>
                        <PostRecordTimeSeconds>5</PostRecordTimeSeconds>
                        <HolidaySchedule>
                            <ScheduleBlock version="1.0">
                                <ScheduleBlockGUID>{00000000-0000-0000-0000-000000000000}</ScheduleBlockGUID>
                                <ScheduleBlockType>www.hikvision.com/racm/schedule/ver10</ScheduleBlockType>
                            </ScheduleBlock>
                        </HolidaySchedule>
                    </CustomExtension>
                </CustomExtensionList>
            </Track>
        </TrackList>
        """
        self.request(method="PUT", url=url, content=xml)


class IpcHttpHandler(BaseHttpHandler):
    def __init__(self, ip):
        super().__init__(ip)
        self.mac = ""

    def login(self, username=nvr_username, password=nvr_password):
        xml_str = self.request(method="GET", url=f"http://:{password}@{self.ip}/ISAPI/Security/sessionLogin/capabilities?username={username}")
        root = ET.fromstring(xml_str)
        session_id = root.find(f"{self.xmlns}sessionID").text  # 临时 session
        salt = root.find(f"{self.xmlns}salt").text
        challenge = root.find(f"{self.xmlns}challenge").text
        iterations = int(root.find(f"{self.xmlns}iterations").text)
        # 计算加密密码
        encode_pwd = PswUtil.encode_pwd(username, password, salt, challenge, iterations)
        self.aes_key = PswUtil.get_aes_key(password, username, salt, iterations)
        # 登录请求
        login_xml = f"""
        <SessionLogin>
            <userName>{username}</userName>
            <password>{encode_pwd}</password>
            <sessionID>{session_id}</sessionID>
            <isSessionIDValidLongTerm>false</isSessionIDValidLongTerm>
            <sessionIDVersion>2</sessionIDVersion>
            <isNeedSessionTag>true</isNeedSessionTag>
        </SessionLogin>
        """
        xml_str = self.request(method="POST", url=f"http://{self.ip}/ISAPI/Security/sessionLogin?timeStamp={int(time.time() * 1000)}", content=login_xml)
        root = ET.fromstring(xml_str)
        self.session_tag = root.find("sessionTag").text  # 真 session

    def set_encode(self):
        url = f"http://{self.ip}/ISAPI/Streaming/channels/101"
        xml = f"""
        <?xml version="1.0" encoding="UTF-8"?>
        <StreamingChannel xmlns="http://www.hikvision.com/ver20/XMLSchema" version="2.0">
            <id>101</id>
            <channelName>Camera 01</channelName>
            <enabled>true</enabled>
            <Transport>
                <maxPacketSize>1000</maxPacketSize>
                <ControlProtocolList>
                    <ControlProtocol>
                        <streamingTransport>RTSP</streamingTransport>
                    </ControlProtocol>
                    <ControlProtocol>
                        <streamingTransport>HTTP</streamingTransport>
                    </ControlProtocol>
                    <ControlProtocol>
                        <streamingTransport>SHTTP</streamingTransport>
                    </ControlProtocol>
                </ControlProtocolList>
                <Unicast>
                    <enabled>true</enabled>
                    <rtpTransportType>RTP/TCP</rtpTransportType>
                </Unicast>
                <Multicast>
                    <enabled>true</enabled>
                    <destIPAddress>0.0.0.0</destIPAddress>
                    <videoDestPortNo>8860</videoDestPortNo>
                    <audioDestPortNo>8862</audioDestPortNo>
                </Multicast>
                <Security>
                    <enabled>true</enabled>
                    <certificateType>digest</certificateType>
                    <SecurityAlgorithm>
                        <algorithmType>MD5</algorithmType>
                    </SecurityAlgorithm>
                </Security>
            </Transport>
            <Audio>
                <enabled>true</enabled>
                <audioInputChannelID>1</audioInputChannelID>
                <audioCompressionType>G.711alaw</audioCompressionType>
            </Audio>
            <Video xmlns="">
                <enabled>true</enabled>
                <videoInputChannelID>1</videoInputChannelID>
                <videoCodecType>H.264</videoCodecType>
                <videoResolutionWidth>1920</videoResolutionWidth>
                <videoScanType>progressive</videoScanType>
                <videoResolutionHeight>1080</videoResolutionHeight>
                <videoQualityControlType>cbr</videoQualityControlType>
                <constantBitRate>1024</constantBitRate>
                <maxFrameRate>2500</maxFrameRate>
                <GovLength>50</GovLength>
                <H264Profile>Main</H264Profile>
                <smoothing>50</smoothing>
                <LBREnabled>true</LBREnabled>
            </Video>
        </StreamingChannel>
        """
        self.request(method="PUT", url=url, content=xml)

    def get_eth_info(self):
        url = f"http://{self.ip}/ISAPI/System/Network/interfaces/1/capabilities"
        xml_str = self.request(method="GET", url=url)
        root = ET.fromstring(xml_str)
        self.mac = root.find(f".//{self.xmlns}MACAddress").text

    def set_ip(self, ip):
        url = f"http://{self.ip}/ISAPI/System/Network/interfaces/1"
        xml = f"""
        <?xml version="1.0" encoding="UTF-8"?>
        <NetworkInterface>
            <id>1</id>
            <IPAddress>
                <ipVersion>dual</ipVersion>
                <addressingType>static</addressingType>
                <ipAddress>{ip}</ipAddress>
                <subnetMask>255.255.255.0</subnetMask>
                <ipV6AddressingType>ra</ipV6AddressingType>
                <DefaultGateway>
                    <ipAddress>192.168.0.1</ipAddress>
                </DefaultGateway>
                <PrimaryDNS>
                    <ipAddress>223.5.5.5</ipAddress>
                </PrimaryDNS>
                <SecondaryDNS>
                    <ipAddress>8.8.8.8</ipAddress>
                </SecondaryDNS>
            </IPAddress>
            <Link>
                <MACAddress>{self.mac}</MACAddress>
                <autoNegotiation>true</autoNegotiation>
                <speed>0</speed>
                <duplex>full</duplex>
                <MTU>1500</MTU>
            </Link>
        </NetworkInterface>
        """
        self.request(method="PUT", url=url, content=xml)

    def reboot(self):
        url = f"http://{self.ip}/ISAPI/System/reboot"
        self.request(method="PUT", url=url)


class InitNVR(QRunnable):
    def __init__(self, signal, ipc_list):
        super().__init__()
        self.signal = signal
        self.ipc_list = ipc_list

    @Slot()
    def run(self):
        nvr = NvrHttpHandler(nvr_ip)
        self.signal.emit(QCoreApplication.translate("InitNVR", "Login NVR backend...", disambiguation=None))
        nvr.login()
        self.signal.emit(QCoreApplication.translate("InitNVR", "Sync local time...", disambiguation=None))
        nvr.set_time()
        ids = nvr.get_ipc_num()
        self.signal.emit(QCoreApplication.translate("InitNVR", "Clear channel list...", disambiguation=None))
        for i in ids:
            nvr.del_ipc(i)
        for ip in self.ipc_list:
            nvr.add_ipc(ip)
            self.signal.emit(QCoreApplication.translate("InitNVR", "Add channel {}...", disambiguation=None).format(ip))
        self.signal.emit(QCoreApplication.translate("InitNVR", "Format disk...", disambiguation=None))
        nvr.format()
        self.signal.emit(QCoreApplication.translate("InitNVR", "NVR initialize finished!", disambiguation=None))


class InitIPC(QRunnable):
    def __init__(self, signal, ipc_list):
        super().__init__()
        self.signal = signal
        self.ipc_list = ipc_list

    @Slot()
    def run(self):
        ipc = IpcHttpHandler(ipc_ip)
        self.signal.emit(QCoreApplication.translate("InitIPC", "Login IPC backend...", disambiguation=None))
        ipc.login()
        self.signal.emit(QCoreApplication.translate("InitIPC", "Sync local time...", disambiguation=None))
        ipc.set_time()
        self.signal.emit(QCoreApplication.translate("InitIPC", "Set video encode to H.264...", disambiguation=None))
        ipc.set_encode()
        ipc.get_eth_info()
        new_ip = self.ipc_list.pop(0)
        ipc.set_ip(new_ip)
        self.signal.emit(QCoreApplication.translate("InitIPC", "Set the IP of the IPC to {}", disambiguation=None).format(new_ip))
        ipc.reboot()
        self.signal.emit(QCoreApplication.translate("InitIPC", "initialize IPC finished! Rebooting... Please wait for IPC started.", disambiguation=None))


class ConfigChannel(QRunnable):
    def __init__(self, signal, channel_num):
        super().__init__()
        self.signal = signal
        self.channel_num = channel_num
        print(f"Channel Nums: {self.channel_num}")

    @Slot()
    def run(self):
        nvr = NvrHttpHandler(nvr_ip)
        self.signal.emit(QCoreApplication.translate("ConfigChannel", "Login NVR backend...", disambiguation=None))
        nvr.login()
        for i in range(1, self.channel_num + 1):
            self.signal.emit(QCoreApplication.translate("ConfigChannel", "Set channel {} encode to H.264...", disambiguation=None).format(i))
            nvr.set_encode(i)
            self.signal.emit(QCoreApplication.translate("ConfigChannel", "Set channel {} event...", disambiguation=None).format(i))
            nvr.config_event(i)
        self.signal.emit(QCoreApplication.translate("ConfigChannel", "All channels config finished!", disambiguation=None))
            # nvr.close_record_scheduler(i) # 新老版本xml差异大，接口报 400


@QmlElement
class Inti(QObject):
    output = Signal(str, arguments=["output"])

    def __init__(self):
        super().__init__()
        self.ipc_list = [ipc_ip]

    @Slot(int)
    def ipcIpGenerator(self, num):
        ip_parts = ipc_ip.split('.')
        base = '.'.join(ip_parts[:3])
        last_octet = int(ip_parts[3])
        self.ipc_list = [f"{base}.{last_octet + num - 1 - i}" for i in range(num)]
        print(self.ipc_list)

    @Slot()
    def initNvr(self):
        logger.info("Initialize NVR...")
        worker = InitNVR(self.output, self.ipc_list)
        threadpool.start(worker)

    @Slot()
    def initIpc(self):
        logger.info("Initialize IPC...")
        worker = InitIPC(self.output, self.ipc_list)
        threadpool.start(worker)

    @Slot(int)
    def configChannel(self, channel_num):
        logger.info("Configurate Channel...")
        worker = ConfigChannel(self.output, channel_num)
        threadpool.start(worker)


# if __name__ == "__main__":
#     # 界面传参
#     ipc_num = 2
#     nvr_ip = "192.168.3.74"
#     ipc_list = ["192.168.3.2", "192.168.3.3"]
#
#     nvr = NvrHttpHandler(nvr_ip, ipc_num)
#     nvr.login()
#     nvr.set_time()
#     ids = nvr.get_ipc_num()
#     for i in ids:
#         nvr.del_ipc(i)
#     for i in ipc_list:
#         nvr.add_ipc(i)
#     nvr.format()
#     # 初始化摄像头
#     for ipc_ip in ipc_list:
#         ipc = IpcHttpHandler(ipc_ip)
#         ipc.login()
#         ipc.set_time()
#         ipc.set_encode()
#         ipc.get_eth_info()
#         ipc.set_ip(ipc_ip)  # 本地测试
#         ipc.reboot()
#
#     time.sleep(60)
#
#     nvr.login()
#     for i in range(1, ipc_num + 1):
#         nvr.set_encode(i)
#         nvr.config_event(i)
#         # nvr.close_record_scheduler(i) # 新老版本xml差异大，接口报 400

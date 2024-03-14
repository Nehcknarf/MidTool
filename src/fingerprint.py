from ctypes import *

from PySide6.QtCore import QObject, QCoreApplication, Property, Signal, Slot, QRunnable, QThreadPool, QThread
from PySide6.QtSerialPort import QSerialPortInfo
from PySide6.QtQml import QmlElement

from utils.log import logger
from utils.adapter import system, root_path
from utils.dictionary import code_dict, new_code_dict


QML_IMPORT_NAME = "src.fingerprint"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0

threadpool = QThreadPool.globalInstance()


class GetFingerprint(QRunnable):
    def __init__(self, signal, storage_id, libc, handle):
        super().__init__()
        self.signal = signal
        self.storage_id = storage_id
        self.libc = libc
        self.handle = handle

    def emit_state(self, code, func_str):
        if code == 0:
            self.signal.emit(QCoreApplication.translate("GetFingerprint", "{} Success").format(func_str))
        else:
            self.signal.emit(QCoreApplication.translate("GetFingerprint", "{} Failed (error type/code: {})").format(func_str, code_dict.get(code, self.libc.ZAZErr2Str(code))))
            return

    @Slot()
    def run(self):
        nAddr = c_int(0xffffffff)
        for i in range(2):
            timeout = 0
            ret = 2  # 传感器上没有手指
            self.signal.emit(QCoreApplication.translate("GetFingerprint", "Please put your finger on the sensor..."))
            while ret == 2 and timeout <= 99:
                ret = self.libc.ZAZGetImage(self.handle, nAddr)
                timeout += 1
                self.signal.emit(QCoreApplication.translate("GetFingerprint", "Collect fingerprint... Attempt {}, return value: {}").format(timeout, code_dict.get(ret, self.libc.ZAZErr2Str(ret))))
            if timeout == 100:
                self.signal.emit(QCoreApplication.translate("GetFingerprint", "Timeout! Please try again"))
                return

            ret = self.libc.ZAZGenChar(self.handle, nAddr, i + 1)
            self.emit_state(ret, QCoreApplication.translate("GetFingerprint", "Generating feature {}").format(i + 1))

            self.signal.emit(QCoreApplication.translate("GetFingerprint", "Please raise your finger!"))
            QThread.sleep(1)

        ret = self.libc.ZAZRegModule(self.handle, nAddr)
        self.emit_state(ret, QCoreApplication.translate("GetFingerprint", "Merge features"))

        if ret == 0:
            ret = self.libc.ZAZStoreChar(self.handle, nAddr, 1, int(self.storage_id))
            self.emit_state(ret, QCoreApplication.translate("GetFingerprint", "Save the fingerprint (flash slot: {})").format(self.storage_id))


class SearchFingerprint(QRunnable):
    def __init__(self, signal, libc, handle):
        super().__init__()
        self.signal = signal
        self.libc = libc
        self.handle = handle

    @Slot()
    def run(self):
        i = c_int(0)
        score = c_int(0)
        nAddr = c_int(0xffffffff)
        ret = 2  # 传感器上没有手指
        timeout = 0
        self.signal.emit(QCoreApplication.translate("SearchFingerprint", "Please put your finger on the sensor..."))
        while ret == 2 and timeout <= 99:
            ret = self.libc.ZAZGetImage(self.handle, nAddr)
            timeout += 1
            self.signal.emit(QCoreApplication.translate("SearchFingerprint", "Collect fingerprint... Attempt {}, return value: {}").format(timeout, code_dict.get(ret, self.libc.ZAZErr2Str(ret))))
        if timeout == 100:
            self.signal.emit(QCoreApplication.translate("SearchFingerprint", "Timeout! Please try again"))
            return

        ret = self.libc.ZAZGenChar(self.handle, nAddr, 1)
        if ret == 0:
            self.signal.emit(QCoreApplication.translate("SearchFingerprint", "Successfully generated features"))
            code = self.libc.ZAZSearch(self.handle, c_int(0xffffffff), 1, 0, 1049, byref(i), byref(score))
            self.signal.emit(QCoreApplication.translate("SearchFingerprint", "***If the return type/code is \"Fingerprint is not found\" and the matching score is 0, then the matched flash slot is not correct. Please just ignore***"))
            self.signal.emit(QCoreApplication.translate("SearchFingerprint", "Start matching (return type/code: {})").format(code_dict.get(code, self.libc.ZAZErr2Str(code))))
            self.signal.emit(QCoreApplication.translate("SearchFingerprint", "Matched flash slot: Not found") if i.value == 65022 else QCoreApplication.translate("SearchFingerprint", "Matched flash slot: {}").format(i.value))
            self.signal.emit(QCoreApplication.translate("SearchFingerprint", "Matching Score: {}").format(score.value))
        else:
            self.signal.emit(QCoreApplication.translate("SearchFingerprint", "Generating features failed (error type/code: {})").format(code_dict.get(ret, self.libc.ZAZErr2Str(ret))))


@QmlElement
class SquareFingerPrint(QObject):
    output = Signal(str, arguments="output")
    getPort = Signal()
    getBaudRate = Signal()

    def __init__(self):
        super().__init__()
        self.handle = c_int64(0)

        if system == "Windows":
            self.libc = cdll.LoadLibrary(f'{root_path}/lib/fingerprint/libapit.dll')
        elif system == "Linux":
            self.libc = cdll.LoadLibrary(f'{root_path}/lib/fingerprint/libapit.so')

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
        self.set_ports([com.portName() for com in QSerialPortInfo.availablePorts()])

    availablePorts = Property(list, get_ports, notify=getPort)

    def get_baud_rates(self):
        return self.baud_rates

    baudRates = Property(list, get_baud_rates, notify=getBaudRate)

    @Slot(str, int, result=int)
    def open_device(self, port_name, baud_rate):
        nDeviceType = 1  # 串口设备
        iCom = int(port_name[-1])  # 串口号 1-16
        iBaud = int(baud_rate / 9600)  # (9600*N)bps,其中N=1—12(默认出厂N=6，即57600bps)
        ret = self.libc.ZAZOpenDeviceEx(byref(self.handle), nDeviceType, iCom, iBaud)
        logger.info(f"(Square Fingerprint) Try to connect fingerprint device through {port_name}@{baud_rate}, return {ret}")
        self.output.emit(self.tr("The fingerprint sensor has opened!") if ret == 0 else self.tr("The fingerprint sensor open failed!"))
        return ret

    @Slot(result=int)
    def close_device(self):
        ret = self.libc.ZAZCloseDeviceEx(self.handle)
        self.output.emit(self.tr("The fingerprint sensor has closed!") if ret in [0, 1] else self.tr("The fingerprint sensor close failed!"))
        return ret

    @Slot(int)
    def get_fingerprint(self, storage_id):
        logger.info("(Square Fingerprint) Try to collect fingerprint...")
        worker = GetFingerprint(self.output, storage_id, self.libc, self.handle)
        threadpool.start(worker)

    @Slot()
    def search_fingerprint(self):
        logger.info("(Square Fingerprint) Try to search fingerprint in database...")
        worker = SearchFingerprint(self.output, self.libc, self.handle)
        threadpool.start(worker)

    @Slot()
    def get_template_num(self):
        num = c_int(0)
        logger.info("(Square Fingerprint) Try to count fingerprints")
        ret = self.libc.ZAZTemplateNum(self.handle, c_int(0xffffffff), byref(num))
        self.output.emit(self.tr("The number of valid fingerprints: {}").format(num.value) if ret == 0 else self.tr("Get the number of valid fingerprints failed"))

    @Slot(int)
    def del_flash(self, storage_id):
        logger.info(f"(Square Fingerprint) Try to del the fingerprint in slot {storage_id}")
        ret = self.libc.ZAZDelChar(self.handle, c_int(0xffffffff), storage_id, 1)
        self.output.emit(self.tr("Successfully delete the fingerprint {}").format(storage_id) if ret == 0 else self.tr("Delete the fingerprint {} failed").format(storage_id))

    @Slot()
    def clean_flash(self):
        logger.info("(Square Fingerprint) Try to clear fingerprint database")
        ret = self.libc.ZAZEmpty(self.handle, c_int(0xffffffff))
        self.output.emit(self.tr("Successfully clear fingerprint database") if ret == 0 else self.tr("Clear Fingerprint database failed"))


class GetFingerprint2(QRunnable):
    def __init__(self, signal, libc):
        super().__init__()
        self.signal = signal
        self.libc = libc

    def emit_state(self, code, func_str):
        if code == 0:
            self.signal.emit(QCoreApplication.translate("GetFingerprint2", "{} Success").format(func_str))
        else:
            self.signal.emit(QCoreApplication.translate("GetFingerprint2", "{} Failed (error type/code: {})").format(func_str, new_code_dict.get(code)))

    @Slot()
    def run(self):
        storage_id = c_int(0)
        for i in range(3):
            timeout = 0
            ret = 40  # 传感器上没有手指
            self.signal.emit(QCoreApplication.translate("GetFingerprint2", "Please put your finger on the sensor..."))
            while ret == 40 and timeout <= 99:
                ret = self.libc.GetImage()
                timeout += 1
                self.signal.emit(QCoreApplication.translate("GetFingerprint2", "Collect fingerprint... Attempt {}, return value: {}").format(timeout, new_code_dict.get(ret)))
            if timeout == 100:
                self.signal.emit(QCoreApplication.translate("GetFingerprint2", "Timeout! Please try again"))
                return

            ret = self.libc.GetChar(i)
            self.emit_state(ret, QCoreApplication.translate("GetFingerprint2", "Generating feature {}").format(i + 1))

            self.signal.emit(QCoreApplication.translate("GetFingerprint2", "Please raise your finger!"))
            QThread.sleep(1)

        ret = self.libc.MergeChar(0, 3)
        self.emit_state(ret, QCoreApplication.translate("GetFingerprint2", "Merge features"))
        if ret == 0:
            ret = self.libc.GetEmptyID(1, 500, byref(storage_id))
            self.emit_state(ret, QCoreApplication.translate("GetFingerprint2", "Get the first available solt in the flash"))
        if ret == 0:
            ret = self.libc.StoreChar(storage_id, 0, 0)
            self.emit_state(ret, QCoreApplication.translate("GetFingerprint2", "Save the fingerprint (flash slot: {})").format(storage_id.value))


class SearchFingerprint2(QRunnable):
    def __init__(self, signal, libc):
        super().__init__()
        self.signal = signal
        self.libc = libc

    @Slot()
    def run(self):
        score = c_int(0)
        storage_id = c_int(0)
        ret = 40  # 传感器上没有手指
        timeout = 0
        self.signal.emit(QCoreApplication.translate("SearchFingerprint2", "Please put your finger on the sensor..."))
        while ret == 40 and timeout <= 99:
            ret = self.libc.GetImage()
            timeout += 1
            self.signal.emit(QCoreApplication.translate("SearchFingerprint2", "Collect fingerprint... Attempt {}, return value: {}").format(timeout, new_code_dict.get(ret)))
        if timeout == 100:
            self.signal.emit(QCoreApplication.translate("SearchFingerprint2", "Timeout! Please try again"))
            return

        ret = self.libc.GetChar(0)
        if ret == 0:
            self.signal.emit(QCoreApplication.translate("SearchFingerprint2", "Successfully generated features"))
            code = self.libc.SearchChar(0, byref(storage_id), byref(score))
            self.signal.emit(QCoreApplication.translate("SearchFingerprint2", "Start matching (return type/code: {})").format(new_code_dict.get(code)))
            self.signal.emit(QCoreApplication.translate("SearchFingerprint2", "Matched flash slot: {}").format(storage_id.value))
            self.signal.emit(QCoreApplication.translate("SearchFingerprint2", "Matching Score: {}").format(score.value * 100))
        else:
            self.signal.emit(QCoreApplication.translate("SearchFingerprint2", "Generating features failed (error type/code: {})").format(new_code_dict.get(ret)))


@QmlElement
class RoundFingerPrint(QObject):
    output = Signal(str, arguments="output")
    getPort = Signal()
    getBaudRate = Signal()

    def __init__(self):
        super().__init__()

        if system == "Linux":
            self.libc = cdll.LoadLibrary(f'{root_path}/lib/fingerprint/lib0a0.so')

        self.ports = [{"value": port.systemLocation(), "text": port.portName()} for port in QSerialPortInfo.availablePorts()]
        self.baud_rates = QSerialPortInfo.standardBaudRates()

    def get_ports(self):
        return self.ports

    def set_ports(self, ports):
        if self.ports != ports:
            self.ports = ports
            self.getPort.emit()

    @Slot()
    def update_ports(self):
        self.set_ports([{"value": port.systemLocation(), "text": port.portName()} for port in QSerialPortInfo.availablePorts()])

    availablePorts = Property(list, get_ports, notify=getPort)

    def get_baud_rates(self):
        return self.baud_rates

    baudRates = Property(list, get_baud_rates, notify=getBaudRate)

    @Slot(str, int, result=int)
    def open_device(self, port_name, baud_rate):
        self.libc.OpenDevice(bytes(port_name, 'utf-8'), baud_rate)
        ret = self.libc.TestConection()
        logger.info(f"(Round Fingerprint) Try to connect fingerprint device through {port_name}@{baud_rate}, return {ret}")
        self.output.emit(self.tr("The fingerprint sensor has opened!") if ret == 0 else self.tr("The fingerprint sensor open failed!"))
        return ret

    @Slot(result=int)
    def close_device(self):
        ret = self.libc.CloseDevice()
        self.output.emit(self.tr("The fingerprint sensor has closed!") if ret == 1 else self.tr("The fingerprint sensor close failed!"))
        return ret

    @Slot()
    def get_fingerprint(self):
        logger.info("(Round Fingerprint) Try to collect fingerprint...")
        worker = GetFingerprint2(self.output, self.libc)
        threadpool.start(worker)

    @Slot()
    def search_fingerprint(self):
        logger.info("(Round Fingerprint) Try to search fingerprint in database...")
        worker = SearchFingerprint2(self.output, self.libc)
        threadpool.start(worker)

    @Slot(int)
    def del_flash(self, storage_id):
        logger.info(f"(Round Fingerprint) Try to del the fingerprint in slot {storage_id}")
        ret = self.libc.DelChar(storage_id, storage_id, 0)
        self.output.emit(self.tr("Successfully delete the fingerprint {}").format(storage_id) if ret == 0 else self.tr("Delete the fingerprint {} failed").format(storage_id))

    @Slot()
    def clean_flash(self):
        logger.info("(Round Fingerprint) Try to clear fingerprint database")
        ret = self.libc.DelChar(1, 500, 0)
        self.output.emit(self.tr("Successfully clear fingerprint database") if ret == 0 else f"{new_code_dict.get(ret)}")

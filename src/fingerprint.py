from ctypes import *

from PySide6.QtCore import QObject, QCoreApplication, Property, Signal, Slot, QRunnable, QThreadPool, QThread
from PySide6.QtSerialPort import QSerialPortInfo
from PySide6.QtQml import QmlElement

from utils.env import system, root_path


QML_IMPORT_NAME = "src.fingerprint"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0

threadpool = QThreadPool.globalInstance()


# 指昂方形指纹模块返回码字典
code_dict = {
    0: QCoreApplication.translate("SquareFingerPrint", "Executed Successfully"),
    1: QCoreApplication.translate("SquareFingerPrint", "Data pacakge error"),
    2: QCoreApplication.translate("SquareFingerPrint", "No finger on the sensor"),
    3: QCoreApplication.translate("SquareFingerPrint", "Collect fingerprint image failed"),
    4: QCoreApplication.translate("SquareFingerPrint", "Fingerprint is too unclear"),
    5: QCoreApplication.translate("SquareFingerPrint", "Fingerprint is too blurry"),
    6: QCoreApplication.translate("SquareFingerPrint", "Fingerprint is too messy"),
    7: QCoreApplication.translate("SquareFingerPrint", "Fingerprint is lack of features"),
    8: QCoreApplication.translate("SquareFingerPrint", "Fingerprint mismatched"),
    9: QCoreApplication.translate("SquareFingerPrint", "Fingerprint is not found"),
    10: QCoreApplication.translate("SquareFingerPrint", "Features merge failed"),
    11: QCoreApplication.translate("SquareFingerPrint", "The number is out of database"),
    12: QCoreApplication.translate("SquareFingerPrint", "Get fingerprint from database failed"),
    13: QCoreApplication.translate("SquareFingerPrint", "Upload feature failed"),
    14: QCoreApplication.translate("SquareFingerPrint", "Module can't receive subsequent data package"),
    15: QCoreApplication.translate("SquareFingerPrint", "Upload image failed"),
    16: QCoreApplication.translate("SquareFingerPrint", "Delete fingerprint failed"),
    17: QCoreApplication.translate("SquareFingerPrint", "Clear fingerprint database failed"),
    18: QCoreApplication.translate("SquareFingerPrint", "Can't enter sleep mode"),
    19: QCoreApplication.translate("SquareFingerPrint", "Incorrect password"),
    20: QCoreApplication.translate("SquareFingerPrint", "Reset system failed"),
    21: QCoreApplication.translate("SquareFingerPrint", "Invalid fingerprint image"),
    -1: QCoreApplication.translate("SquareFingerPrint", "Send failed"),
    -2: QCoreApplication.translate("SquareFingerPrint", "Receive failed")
}


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
        self.signal.emit(QCoreApplication.translate("GetFingerprint", "Please put your finger on the sensor..."))
        ret = 2  # 传感器上没有手指
        timeout = 0
        while ret == 2 and timeout <= 99:
            # QApplication.processEvents()
            self.signal.emit(QCoreApplication.translate("GetFingerprint", "Collect fingerprint... Attempt {}, return value: {}").format(timeout + 1, code_dict.get(ret, self.libc.ZAZErr2Str(ret))))
            ret = self.libc.ZAZGetImage(self.handle, nAddr)
            timeout += 1
        if timeout == 100:
            self.signal.emit(QCoreApplication.translate("GetFingerprint", "Timeout! Please try again"))
            return
        self.emit_state(ret, QCoreApplication.translate("GetFingerprint", "First round"))

        ret = self.libc.ZAZGenChar(self.handle, nAddr, 2)
        self.emit_state(ret, QCoreApplication.translate("GetFingerprint", "Generating feature A"))

        self.signal.emit(QCoreApplication.translate("GetFingerprint", "Please raise your finger!"))
        self.signal.emit(QCoreApplication.translate("GetFingerprint", "Please put your finger on sensor again..."))

        ret = 2  # 传感器上没有手指
        timeout = 0
        while ret == 2 and timeout <= 99:
            # QApplication.processEvents()
            self.signal.emit(QCoreApplication.translate("GetFingerprint", "Collect fingerprint... Attempt {}, return value: {}").format(timeout + 1, code_dict.get(ret, self.libc.ZAZErr2Str(ret))))
            ret = self.libc.ZAZGetImage(self.handle, nAddr)
            timeout += 1
        if timeout == 100:
            self.signal.emit(QCoreApplication.translate("GetFingerprint", "Timeout! Please try again"))
            return
        self.emit_state(ret, QCoreApplication.translate("GetFingerprint", "Second round"))

        ret = self.libc.ZAZGenChar(self.handle, nAddr, 1)
        self.emit_state(ret, QCoreApplication.translate("GetFingerprint", "Generating feature B"))

        ret = self.libc.ZAZRegModule(self.handle, nAddr)
        self.emit_state(ret, QCoreApplication.translate("GetFingerprint", "Merge features"))

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
        self.signal.emit(QCoreApplication.translate("SearchFingerprint", "Please put your finger on the sensor..."))
        i = c_int(0)
        score = c_int(0)
        nAddr = c_int(0xffffffff)
        ret = 2  # 传感器上没有手指
        timeout = 0
        while ret == 2 and timeout <= 99:
            self.signal.emit(QCoreApplication.translate("SearchFingerprint", "Collect fingerprint... Attempt {}, return value: {}")
                             .format(timeout + 1, code_dict.get(ret, self.libc.ZAZErr2Str(ret))))
            ret = self.libc.ZAZGetImage(self.handle, nAddr)
            timeout += 1
        if timeout == 100:
            self.signal.emit(QCoreApplication.translate("SearchFingerprint", "Timeout! Please try again"))
            # self.close_device()
            return
        if ret == 0:
            self.signal.emit(QCoreApplication.translate("SearchFingerprint", "Collect fingerprint successfully"))
        else:
            self.signal.emit(QCoreApplication.translate("SearchFingerprint", "Collect fingerprint failed"))
            # self.close_device()
            return

        ret = self.libc.ZAZGenChar(self.handle, nAddr, 1)
        if ret == 0:
            self.signal.emit(QCoreApplication.translate("SearchFingerprint", "Successfully generated features"))
            code = self.libc.ZAZSearch(self.handle, c_int(0xffffffff), 1, 0, 1049, byref(i), byref(score))
            self.signal.emit(QCoreApplication.translate("SearchFingerprint", "***If the return type/code is \"Fingerprint is not found\" and the matching score is 0, then the matched ID is not correct. Please just ignore***"))
            self.signal.emit(QCoreApplication.translate("SearchFingerprint", "Return type/code: {}").format(code_dict.get(code, self.libc.ZAZErr2Str(code))))
            self.signal.emit(QCoreApplication.translate("SearchFingerprint", "Matching ID: Not found") if i.value == 65022 else self.tr("Matching ID: {}").format(str(i.value)))
            self.signal.emit(QCoreApplication.translate("SearchFingerprint", "Matching Score: {}").format(str(score.value)))
        else:
            self.signal.emit(QCoreApplication.translate("SearchFingerprint", "Generating features failed (error type/code: {})").format(code_dict.get(ret, self.libc.ZAZErr2Str(ret))))


@QmlElement
class SquareFingerPrint(QObject):
    comChanged = Signal()
    Output = Signal(str)

    def __init__(self):
        super().__init__()
        if system == "Windows":
            self.libc = cdll.LoadLibrary(f'{root_path}/lib/fingerprint/libapit.dll')
        elif system == "Linux":
            self.libc = cdll.LoadLibrary(f'{root_path}/lib/fingerprint/libapit.so')
        self.handle = c_int64(0)

    def get_ports(self):
        com_model = [com.portName() for com in QSerialPortInfo.availablePorts()]
        return com_model

    def get_baud_rates(self):
        return QSerialPortInfo.standardBaudRates()

    coms = Property(list, get_ports, notify=comChanged)
    baud_rates = Property(list, get_baud_rates, notify=comChanged)

    @Slot(str, int, result=int)
    def open_device(self, port_name, baud_rate):
        nDeviceType = 1  # 串口设备
        iCom = int(port_name[-1])  # 串口号 1-16
        iBaud = int(baud_rate / 9600)  # (9600*N)bps,其中N=1—12(默认出厂N=6，即57600bps)

        ret = self.libc.ZAZOpenDeviceEx(byref(self.handle), nDeviceType, iCom, iBaud)
        self.Output.emit(self.tr("The fingerprint sensor has opened! {}").format(ret) if ret == 0 else self.tr("The fingerprint sensor open failed! {}").format(ret))
        return ret

    @Slot(result=int)
    def close_device(self):
        ret = self.libc.ZAZCloseDeviceEx(self.handle)
        self.Output.emit(self.tr("The fingerprint sensor has closed! {}").format(ret) if ret in [0, 1] else self.tr("The fingerprint sensor close failed! {}").format(ret))
        return ret

    @Slot(int)
    def get_fingerprint(self, storage_id):
        worker = GetFingerprint(self.Output, storage_id, self.libc, self.handle)
        threadpool.start(worker)

    @Slot()
    def search_fingerprint(self):
        worker = SearchFingerprint(self.Output, self.libc, self.handle)
        threadpool.start(worker)

    @Slot()
    def get_template_num(self):
        num = c_int(0)
        ret = self.libc.ZAZTemplateNum(self.handle, c_int(0xffffffff), byref(num))
        self.Output.emit(self.tr("The number of valid fingerprints: {}").format(num.value) if ret == 0 else self.tr("Get the number of valid fingerprints failed"))

    @Slot(int)
    def del_flash(self, storage_id):
        ret = self.libc.ZAZDelChar(self.handle, c_int(0xffffffff), storage_id, 1)
        self.Output.emit(self.tr("Successfully delete the fingerprint {}").format(storage_id) if ret == 0 else self.tr("Delete the fingerprint {} failed").format(storage_id))

    @Slot()
    def clean_flash(self):
        ret = self.libc.ZAZEmpty(self.handle, c_int(0xffffffff))
        self.Output.emit(self.tr("Successfully clear fingerprint database") if ret == 0 else self.tr("Clear Fingerprint database failed"))


# 指昂圆形指纹模块返回码字典
new_code_dict = {
    0: QCoreApplication.translate("RoundFingerPrint", "Process successfully"),
    1: QCoreApplication.translate("RoundFingerPrint", "Process failed"),
    16: QCoreApplication.translate("RoundFingerPrint", "1:1 match fingerprint with specified template failed"),
    17: QCoreApplication.translate("RoundFingerPrint", "1:N comparison has been conducted, but there are no matching template"),
    18: QCoreApplication.translate("RoundFingerPrint", "There is no registered template within the specified number"),
    19: QCoreApplication.translate("RoundFingerPrint", "Template already exists within the specified range"),
    20: QCoreApplication.translate("RoundFingerPrint", "There is no registered template"),
    21: QCoreApplication.translate("RoundFingerPrint", "There is no template ID that can be registered"),
    22: QCoreApplication.translate("RoundFingerPrint", "There is no corrupted template"),
    23: QCoreApplication.translate("RoundFingerPrint", "The specified template data is invalid"),
    24: QCoreApplication.translate("RoundFingerPrint", "The fingerprint is already registered"),
    25: QCoreApplication.translate("RoundFingerPrint", "Fingerprint image quality is poor"),
    26: QCoreApplication.translate("RoundFingerPrint", "Merge Template failed"),
    27: QCoreApplication.translate("RoundFingerPrint", "Communication password confirmation is not conducted"),
    28: QCoreApplication.translate("RoundFingerPrint", "Burn external flash error"),
    29: QCoreApplication.translate("RoundFingerPrint", "The specified template number is invalid"),
    34: QCoreApplication.translate("RoundFingerPrint", "Incorrect parameters are used"),
    35: QCoreApplication.translate("RoundFingerPrint", "Timeout, no fingerprint input"),
    37: QCoreApplication.translate("RoundFingerPrint", "The number of combined fingerprints is invalid"),
    38: QCoreApplication.translate("RoundFingerPrint", "Buffer ID value is incorrect"),
    40: QCoreApplication.translate("RoundFingerPrint", "There is no fingerprint input on the sensor"),
    65: QCoreApplication.translate("RoundFingerPrint", "Instruction is cancelled"),
    -1: QCoreApplication.translate("RoundFingerPrint", "Send failed")
}


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
            while ret != 0 and timeout <= 9:
                ret = self.libc.GetImage()
                self.signal.emit(QCoreApplication.translate("GetFingerprint2", "Collect fingerprint... Attempt {}, return value: {}").format(timeout + 1, new_code_dict.get(ret)))
                QThread.sleep(1)
                timeout += 1
            if ret != 0:
                break

            ret = self.libc.GetChar(i)
            self.emit_state(ret, QCoreApplication.translate("GetFingerprint2", "Generating feature {}").format(i + 1))
            self.signal.emit(QCoreApplication.translate("GetFingerprint2", "Please raise your finger!"))

        ret = self.libc.MergeChar(0, 3)
        self.emit_state(ret, QCoreApplication.translate("GetFingerprint2", "Merge features"))
        ret = self.libc.GetEmptyID(1, 500, byref(storage_id))
        self.emit_state(ret, QCoreApplication.translate("GetFingerprint2", "Get the first available solt in the flash"))
        ret = self.libc.StoreChar(storage_id, 0, 0)
        self.emit_state(ret, QCoreApplication.translate("GetFingerprint2", "Save the fingerprint (flash slot: {})").format(storage_id.value))


class SearchFingerprint2(QRunnable):
    def __init__(self, signal, libc):
        super().__init__()
        self.signal = signal
        self.libc = libc

    @Slot()
    def run(self):
        self.signal.emit(QCoreApplication.translate("SearchFingerprint2", "Please put your finger on the sensor..."))
        storage_id = c_int(0)
        score = c_int(0)
        timeout = 0
        ret = 40  # 传感器上没有手指
        while ret != 0 and timeout <= 9:
            ret = self.libc.GetImage()
            self.signal.emit(f"{new_code_dict.get(ret)}")
            QThread.sleep(1)
            timeout += 1
        ret = self.libc.GetChar(0)
        if ret == 0:
            self.signal.emit(QCoreApplication.translate("SearchFingerprint2", "Successfully generated features"))
            ret = self.libc.SearchChar(0, byref(storage_id), byref(score))
            self.signal.emit(QCoreApplication.translate("SearchFingerprint2", "Start matching (return type/code: {})").format(new_code_dict.get(ret)))
            self.signal.emit(QCoreApplication.translate("SearchFingerprint2", "Matched flash slot: {}").format(storage_id.value))
            self.signal.emit(QCoreApplication.translate("SearchFingerprint2", "Matching Score: {}").format(score.value * 100))
        else:
            self.signal.emit(QCoreApplication.translate("SearchFingerprint2", "Generating features failed (error type/code: {})").format(new_code_dict.get(ret)))


@QmlElement
class RoundFingerPrint(QObject):
    comChanged = Signal()
    Output = Signal(str)

    def __init__(self):
        super().__init__()
        if system == "Linux":
            self.libc = cdll.LoadLibrary(f'{root_path}/lib/fingerprint/lib0a0.so')

    def get_ports(self):
        com_model = [
            {"value": com.systemLocation(), "text": com.portName()}
            for com in QSerialPortInfo.availablePorts()
        ]
        return com_model

    def get_baud_rates(self):
        return QSerialPortInfo.standardBaudRates()

    coms = Property(list, get_ports, notify=comChanged)
    baud_rates = Property(list, get_baud_rates, notify=comChanged)

    @Slot(str, int, result=int)
    def open_device(self, port_name, baud_rate):
        self.libc.OpenDevice(bytes(port_name, 'utf-8'), baud_rate)
        ret = self.libc.TestConection()
        self.Output.emit(self.tr("The fingerprint sensor has opened! {}").format(ret) if ret == 0 else self.tr("The fingerprint sensor open failed! {}").format(ret))
        return ret

    @Slot(result=int)
    def close_device(self):
        ret = self.libc.CloseDevice()
        self.Output.emit(self.tr("The fingerprint sensor has closed! {}").format(ret) if ret == 1 else self.tr("The fingerprint sensor close failed! {}").format(ret))
        return ret

    @Slot()
    def get_fingerprint(self):
        worker = GetFingerprint2(self.Output, self.libc)
        threadpool.start(worker)

    @Slot()
    def search_fingerprint(self):
        worker = SearchFingerprint2(self.Output, self.libc)
        threadpool.start(worker)

    @Slot(int)
    def del_flash(self, storage_id):
        ret = self.libc.DelChar(storage_id, storage_id, 0)
        self.Output.emit(self.tr("Successfully delete the fingerprint {}").format(storage_id) if ret == 0 else self.tr("Delete the fingerprint {} failed").format(storage_id))

    @Slot()
    def clean_flash(self):
        ret = self.libc.DelChar(1, 500, 0)
        self.Output.emit(f"{new_code_dict.get(ret)}")

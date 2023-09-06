from ctypes import *

from PySide6.QtCore import QObject, QCoreApplication, Property, Signal, Slot, QRunnable, QThreadPool, QThread
from PySide6.QtSerialPort import QSerialPortInfo
from PySide6.QtQml import QmlElement

from utils.env import system, root_path
from utils.mapper import code_dict, new_code_dict


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
            self.signal.emit(QCoreApplication.translate("GetFingerprint", "{}成功").format(func_str))
        else:
            self.signal.emit(QCoreApplication.translate("GetFingerprint", "{}失败(错误类型/代码：{})").format(func_str, code_dict.get(code, self.libc.ZAZErr2Str(code))))
            return

    @Slot()
    def run(self):
        nAddr = c_int(0xffffffff)
        self.signal.emit(QCoreApplication.translate("GetFingerprint", "请将手指平放在传感器上..."))
        ret = 2  # 传感器上没有手指
        timeout = 0
        while ret == 2 and timeout <= 99:
            # QApplication.processEvents()
            self.signal.emit(QCoreApplication.translate("GetFingerprint", "获取指纹图像中...第{}次尝试，返回值：{}").format(timeout + 1, code_dict.get(ret, self.libc.ZAZErr2Str(ret))))
            ret = self.libc.ZAZGetImage(self.handle, nAddr)
            timeout += 1
        if timeout == 100:
            self.signal.emit(QCoreApplication.translate("GetFingerprint", "超时！请重新采集"))
            return
        self.emit_state(ret, QCoreApplication.translate("GetFingerprint", "第一次采集指纹"))

        ret = self.libc.ZAZGenChar(self.handle, nAddr, 2)
        self.emit_state(ret, QCoreApplication.translate("GetFingerprint", "生成特征A"))

        self.signal.emit(QCoreApplication.translate("GetFingerprint", "请抬起手指！"))
        self.signal.emit(QCoreApplication.translate("GetFingerprint", "请再次将手指平放在传感器上..."))

        ret = 2  # 传感器上没有手指
        timeout = 0
        while ret == 2 and timeout <= 99:
            # QApplication.processEvents()
            self.signal.emit(QCoreApplication.translate("GetFingerprint", "获取指纹图像中...第{}次尝试，返回值：{}").format(timeout + 1, code_dict.get(ret, self.libc.ZAZErr2Str(ret))))
            ret = self.libc.ZAZGetImage(self.handle, nAddr)
            timeout += 1
        if timeout == 100:
            self.signal.emit(QCoreApplication.translate("GetFingerprint", "超时！请重新采集"))
            return
        self.emit_state(ret, QCoreApplication.translate("GetFingerprint", "第二次采集指纹"))

        ret = self.libc.ZAZGenChar(self.handle, nAddr, 1)
        self.emit_state(ret, QCoreApplication.translate("GetFingerprint", "生成特征B"))

        ret = self.libc.ZAZRegModule(self.handle, nAddr)
        self.emit_state(ret, QCoreApplication.translate("GetFingerprint", "合并特征"))

        ret = self.libc.ZAZStoreChar(self.handle, nAddr, 1, int(self.storage_id))
        self.emit_state(ret, QCoreApplication.translate("GetFingerprint", "保存模板(位置{})").format(self.storage_id))


class SearchFingerprint(QRunnable):
    def __init__(self, signal, libc, handle):
        super().__init__()
        self.signal = signal
        self.libc = libc
        self.handle = handle

    @Slot()
    def run(self):
        self.signal.emit(QCoreApplication.translate("SearchFingerprint", "请将手指平放在传感器上..."))
        i = c_int(0)
        score = c_int(0)
        nAddr = c_int(0xffffffff)
        ret = 2  # 传感器上没有手指
        timeout = 0
        while ret == 2 and timeout <= 99:
            self.signal.emit(QCoreApplication.translate("SearchFingerprint", "获取指纹图像中...第{}次尝试，返回值：{}")
                             .format(timeout + 1, code_dict.get(ret, self.libc.ZAZErr2Str(ret))))
            ret = self.libc.ZAZGetImage(self.handle, nAddr)
            timeout += 1
        if timeout == 100:
            self.signal.emit(QCoreApplication.translate("SearchFingerprint", "超时！请重新采集"))
            # self.close_device()
            return
        if ret == 0:
            self.signal.emit(QCoreApplication.translate("SearchFingerprint", "成功获取指纹"))
        else:
            self.signal.emit(QCoreApplication.translate("SearchFingerprint", "获取指纹失败"))
            # self.close_device()
            return

        ret = self.libc.ZAZGenChar(self.handle, nAddr, 1)
        if ret == 0:
            self.signal.emit(QCoreApplication.translate("SearchFingerprint", "生成特征成功"))
            code = self.libc.ZAZSearch(self.handle, c_int(0xffffffff), 1, 0, 1049, byref(i), byref(score))
            self.signal.emit(QCoreApplication.translate("SearchFingerprint", "***如果返回类型/代码为”没搜索到指纹“，且匹配得分为0，则匹配得到的ID不正确，忽略即可***"))
            self.signal.emit(QCoreApplication.translate("SearchFingerprint", "返回类型/代码：{}").format(code_dict.get(code, self.libc.ZAZErr2Str(code))))
            self.signal.emit(QCoreApplication.translate("SearchFingerprint", "匹配的ID：未找到") if i.value == 65022 else self.tr("匹配的ID：{}").format(str(i.value)))
            self.signal.emit(QCoreApplication.translate("SearchFingerprint", "匹配得分：{}").format(str(score.value)))
        else:
            self.signal.emit(QCoreApplication.translate("SearchFingerprint", "生成特征失败(错误类型/代码：{})").format(code_dict.get(ret, self.libc.ZAZErr2Str(ret))))


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
        self.Output.emit(self.tr("设备已打开！{}").format(ret) if ret == 0 else self.tr("设备未正确打开！{}").format(ret))
        return ret

    @Slot(result=int)
    def close_device(self):
        ret = self.libc.ZAZCloseDeviceEx(self.handle)
        self.Output.emit(self.tr("设备已关闭！{}").format(ret) if ret in [0, 1] else self.tr("设备未正确关闭！{}").format(ret))
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
        self.Output.emit(self.tr("有效模板总数为{}").format(num.value) if ret == 0 else self.tr("获取有效模板总数失败"))

    @Slot(int)
    def del_flash(self, storage_id):
        ret = self.libc.ZAZDelChar(self.handle, c_int(0xffffffff), storage_id, 1)
        self.Output.emit(self.tr("模板{}删除成功").format(storage_id) if ret == 0 else self.tr("模板{}删除失败").format(storage_id))

    @Slot()
    def clean_flash(self):
        ret = self.libc.ZAZEmpty(self.handle, c_int(0xffffffff))
        self.Output.emit(self.tr("成功清空指纹库") if ret == 0 else self.tr("清空指纹库失败"))


class GetFingerprint2(QRunnable):
    def __init__(self, signal, libc):
        super().__init__()
        self.signal = signal
        self.libc = libc

    def emit_state(self, code, func_str):
        if code == 0:
            self.signal.emit(QCoreApplication.translate("GetFingerprint2", "{}成功").format(func_str))
        else:
            self.signal.emit(QCoreApplication.translate("GetFingerprint2", "{}失败(错误类型/代码：{})").format(func_str, new_code_dict.get(code)))

    @Slot()
    def run(self):
        storage_id = c_int(0)
        for i in range(3):
            timeout = 0
            ret = 40  # 传感器上没有手指
            self.signal.emit(QCoreApplication.translate("GetFingerprint2", "请将手指平放在传感器上..."))
            while ret != 0 and timeout <= 9:
                ret = self.libc.GetImage()
                self.signal.emit(QCoreApplication.translate("GetFingerprint2", "第{}次尝试，{}").format(timeout + 1, new_code_dict.get(ret)))
                QThread.sleep(1)
                timeout += 1
            if ret != 0:
                break

            ret = self.libc.GetChar(i)
            self.emit_state(ret, QCoreApplication.translate("GetFingerprint2", "生成特征{}").format(i + 1))
            self.signal.emit(QCoreApplication.translate("GetFingerprint2", "请抬起手指！"))

        ret = self.libc.MergeChar(0, 3)
        self.emit_state(ret, QCoreApplication.translate("GetFingerprint2", "合并特征"))
        ret = self.libc.GetEmptyID(1, 500, byref(storage_id))
        self.emit_state(ret, QCoreApplication.translate("GetFingerprint2", "获取首个可注册模板位置"))
        ret = self.libc.StoreChar(storage_id, 0, 0)
        self.emit_state(ret, QCoreApplication.translate("GetFingerprint2", "保存模板(位置{})").format(storage_id.value))


class SearchFingerprint2(QRunnable):
    def __init__(self, signal, libc):
        super().__init__()
        self.signal = signal
        self.libc = libc

    @Slot()
    def run(self):
        self.signal.emit(QCoreApplication.translate("SearchFingerprint2", "请将手指平放在传感器上..."))
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
            self.signal.emit(QCoreApplication.translate("SearchFingerprint2", "生成特征成功"))
            ret = self.libc.SearchChar(0, byref(storage_id), byref(score))
            self.signal.emit(QCoreApplication.translate("SearchFingerprint2", "进行比对(返回类型/代码：{})").format(new_code_dict.get(ret)))
            self.signal.emit(QCoreApplication.translate("SearchFingerprint2", "匹配的模板位置：{}").format(storage_id.value))
            self.signal.emit(QCoreApplication.translate("SearchFingerprint2", "匹配得分：{}").format(score.value * 100))
        else:
            self.signal.emit(QCoreApplication.translate("SearchFingerprint2", "生成特征失败(错误类型/代码：{})").format(new_code_dict.get(ret)))


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
        self.Output.emit(self.tr("设备已打开！{}").format(ret) if ret == 0 else self.tr("设备未正确打开！{}").format(ret))
        return ret

    @Slot(result=int)
    def close_device(self):
        ret = self.libc.CloseDevice()
        self.Output.emit(self.tr("设备已关闭！{}").format(ret) if ret == 1 else self.tr("设备未正确关闭！{}").format(ret))
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
        self.Output.emit(self.tr("模板{}删除成功").format(storage_id) if ret == 0 else self.tr("模板{}删除失败").format(storage_id))

    @Slot()
    def clean_flash(self):
        ret = self.libc.DelChar(1, 500, 0)
        self.Output.emit(f"{new_code_dict.get(ret)}")

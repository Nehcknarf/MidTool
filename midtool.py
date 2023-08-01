import os
import sys
import platform
import re
import glob
import json
import random
import logging
import struct
from ctypes import *
from datetime import datetime

from ruamel.yaml import YAML

import PySide2.QtQuick
from PySide2.QtMultimedia import QCameraInfo, QCamera, QCameraViewfinderSettings, QCameraImageCapture
from PySide2.QtMultimediaWidgets import QCameraViewfinder
from PySide2.QtNetwork import QLocalSocket, QLocalServer
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication, QWidget, QFileDialog, QInputDialog, QMessageBox, QLineEdit, \
    QTableWidgetItem, QHeaderView
from PySide2.QtCore import Qt, QThread, Signal, QIODevice, QProcess, QCoreApplication, QCommandLineParser, \
    QCommandLineOption, QTranslator, QLocale, QObject, QRunnable, Slot, QThreadPool, QRegExp, QTimer
from PySide2.QtGui import QIcon, QGuiApplication, QRegExpValidator
from PySide2.QtSerialPort import QSerialPortInfo, QSerialPort

import qrc


# DEBUG
# os.environ["QT_DEBUG_PLUGINS"] = "1"
# 虚拟键盘
os.environ["QT_IM_MODULE"] = "qtvirtualkeyboard"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(level=logging.WARN)

path = os.path.abspath(os.path.dirname(__file__))

# 指昂方形指纹模块返回码字典
code_dict = {0: "执行成功", 1: "数据包接收错误", 2: "传感器上没有手指", 3: "录入指纹图象失败", 4: "指纹太淡", 5: "指纹太糊",
             6: "指纹太乱", 7: "指纹特征点太少", 8: "指纹不匹配", 9: "没搜索到指纹", 10: "特征合并失败", 11: "地址号超出指纹库范围",
             12: "从指纹库读模板出错", 13: "上传特征失败", 14: "模块不能接收后续数据包", 15: "上传图象失败", 16: "删除模板失败",
             17: "清空指纹库失败", 18: "不能进入休眠", 19: "口令不正确", 20: "系统复位失败", 21: "无效指纹图象",
             -1: "发送失败", -2: "接收失败"}

# 指昂圆形指纹模块返回码字典
new_code_dict = {0: "处理成功", 1: "处理失败", 16: "与指定编号中模板的1:1比对失败", 17: "已进行1:N比对，但相同模板不存在",
                 18: "在指定编号中不存在已注册的模板", 19: "在指定编号中已存在模板", 20: "不存在已注册的模板",
                 21: "不存在可注册的模板ID", 22: "不存在已损坏的模板", 23: "指定的模板数据无效", 24: "该指纹已注册",
                 25: "指纹图像质量不好", 26: "模板合成失败", 27: "没有进行通讯密码确认", 28: "外部Flash烧写出错",
                 29: "指定模板编号无效", 34: "使用了不正确的参数", 35: "超时，没有输入指纹", 37: "指纹合成个数无效",
                 38: "Buffer ID值不正确", 40: "采集器上没有指纹输入", 65: "指令被取消", -1: "发送失败"}

device_dict = {"0708": "身份RFID读卡器类", "0107": "条码扫描头类", "020a": "人体感应类"}

# 线程池
threadpool = QThreadPool.globalInstance()


class WorkerSignals(QObject):
    stdout = Signal(str)
    verbose = Signal(str)
    context = Signal(str)
    step = Signal(str)
    pinout = Signal(str)


class General(QRunnable):
    def __init__(self, func, *args):
        super().__init__()
        self.signals = WorkerSignals()
        self.func = func
        self.args = args

    @Slot()
    def run(self):
        ret = self.func(*self.args)
        self.signals.step.emit(ret)


class Commander(QRunnable):
    def __init__(self, command, password=None, wd="/nubomed"):
        super().__init__()
        self.signals = WorkerSignals()
        self.need_kill = False
        self.command = command
        self.password = password
        self.wd = wd

    @Slot()
    def run(self):
        process_command = QProcess()
        process_command.setProcessChannelMode(QProcess.MergedChannels)
        if self.command.__contains__("sudo"):
            # Pipe
            process_echo = QProcess()
            process_echo.setStandardOutputProcess(process_command)
            process_echo.setProgram("echo")
            process_echo.setArguments(self.password)
            process_echo.start()
            # process_echo.start(f"echo {self.password}")
            process_echo.waitForFinished()

        if system == "Linux":
            process_command.setWorkingDirectory(self.wd)
        process_command.setProgram(self.command.split()[0])
        process_command.setArguments(self.command.split()[1:])
        process_command.start()
        # process_command.start(self.command)
        process_command.waitForStarted()
        string = ""
        while process_command.state() != QProcess.NotRunning:
            # QApplication.processEvents()
            # if QThread.currentThread().isInterruptionRequested():
            if self.need_kill:
                break
            if process_command.waitForReadyRead():
                if system == "Windows":
                    stdout = bytes(process_command.readAllStandardOutput()).decode("gbk").rstrip('\r\n')
                elif system == "Linux":
                    stdout = bytes(process_command.readAllStandardOutput()).decode("utf8").rstrip('\n')
                self.signals.stdout.emit(stdout)
                string += f"{stdout}\n"

        self.signals.verbose.emit(string)
        self.signals.stdout.emit("指令已执行")

    def kill(self):
        self.need_kill = True


class Serial(QRunnable):
    def __init__(self, ser):
        super().__init__()
        self.signals = WorkerSignals()
        self.ser = ser
        self.total_data = b''

    @Slot()
    def run(self):
        bytes_data = self.ser.readAll().data()  # bytes
        self.total_data += bytes_data
        self.signals.pinout.emit("数据流：" + self.total_data.hex() + "字符串：" + str(self.total_data))
        if length_domain := re.findall(b'~(.{2})\x02', self.total_data):
            try:
                length = struct.unpack("h", length_domain[0])[0] + 4  # 版本号到数据域的长度 + 长度域 + 校验域 = 总长度
            except struct.error as err:
                print(f"长度域解析失败，{err}")
            else:
                if pack_data := re.findall(b'~.{'+f'{length}'.encode()+b'}\xe7', self.total_data, re.DOTALL):
                    pack_data = pack_data[0]
                    # self.signals.pinout.emit("接收到的原始数据包：" + pack_data.hex())
                    try:
                        header_tuple = struct.unpack("<chc4s4s2h2scB2s2ch", pack_data[:26])  # 起始域到参数长度域
                    except struct.error as err:
                        print(f"数据头解析失败，{err}")
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
                                sig_data = f"数据载荷解析失败，{err}"
                            else:
                                # 自动上报RFID号
                                card_type = payload_tuple[0]
                                card_uid = "-".join(map(str, payload_tuple[1:]))
                                sig_data = f"设备类型：{device_dict.get(device_type)}，卡类型：{card_type}，卡号：{card_uid}"
                        elif device_type == "0107":
                            try:
                                payload_tuple = struct.unpack(f"{payload_length}B", pack_data[26:26 + payload_length])
                                # ending_tuple = struct.unpack("2sc", pack_data[26 + payload_length:29 + payload_length])
                            except struct.error as err:
                                sig_data = f"数据载荷解析失败，{err}"
                            else:
                                # ending_list = [i.hex() for i in ending_tuple]
                                # unpack_data = tuple(header_list) + payload_tuple + tuple(ending_list)
                                # print(unpack_data)
                                # 自动上报扫描码内容
                                code_content = "".join(map(str, payload_tuple[2:]))
                                sig_data = f"设备类型：{device_dict.get(device_type)}，条码内容：{code_content}"
                        elif device_type == "020a":
                            try:
                                payload_tuple = struct.unpack(f"{payload_length}B", pack_data[26:26 + payload_length])
                            except struct.error as err:
                                sig_data = f"数据载荷解析失败，{err}"
                            else:
                                # 自动上报人位置状态变化
                                state_dict = {1: "人在指定范围内", 0: "人离开了指定范围"}
                                sig_data = f"设备类型：{device_dict.get(device_type)}，{state_dict.get(payload_tuple[0])}"
                        else:
                            sig_data = "尚未支持解析的设备类型"
                        self.signals.pinout.emit(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')}，{sig_data}")
                else:
                    pass
                    # self.signals.pinout.emit("未匹配到数据包")
        else:
            self.total_data = b''
            # self.signals.pinout.emit("未找到特征（长度域）")


class GetFingerprint(QRunnable):
    def __init__(self, storage_id, dll, handle):
        super().__init__()
        self.signals = WorkerSignals()
        self.storage_id = storage_id
        self.libc = dll
        self.handle = handle

    def emit_state(self, code, func_str):
        if code == 0:
            self.signals.step.emit(f"{func_str}成功")
        else:
            self.signals.step.emit(f"{func_str}失败(错误类型/代码：{code_dict.get(code, self.libc.ZAZErr2Str(code))})")
            return

    @Slot()
    def run(self):
        nAddr = c_int(0xffffffff)
        self.signals.step.emit("请将手指平放在传感器上...")
        ret = 2  # 传感器上没有手指
        timeout = 0
        while ret == 2 and timeout <= 99:
            # QApplication.processEvents()
            self.signals.step.emit(f"获取指纹图像中...第{timeout + 1}次尝试，返回值：{code_dict.get(ret, self.libc.ZAZErr2Str(ret))}")
            ret = self.libc.ZAZGetImage(self.handle, nAddr)
            timeout += 1
        if timeout == 100:
            self.signals.step.emit("超时！请重新采集")
            return
        self.emit_state(ret, "第一次采集指纹")

        ret = self.libc.ZAZGenChar(self.handle, nAddr, 2)
        self.emit_state(ret, "生成特征A")

        self.signals.step.emit("请抬起手指！")
        QThread.sleep(1)
        self.signals.step.emit("请再次将手指平放在传感器上...")

        ret = 2  # 传感器上没有手指
        timeout = 0
        while ret == 2 and timeout <= 99:
            # QApplication.processEvents()
            self.signals.step.emit(f"获取指纹图像中...第{timeout + 1}次尝试，返回值：{code_dict.get(ret, self.libc.ZAZErr2Str(ret))}")
            ret = self.libc.ZAZGetImage(self.handle, nAddr)
            timeout += 1
        if timeout == 100:
            self.signals.step.emit("超时！请重新采集")
            return
        self.emit_state(ret, "第二次采集指纹")

        ret = self.libc.ZAZGenChar(self.handle, nAddr, 1)
        self.emit_state(ret, "生成特征B")

        ret = self.libc.ZAZRegModule(self.handle, nAddr)
        self.emit_state(ret, "合并特征")

        ret = self.libc.ZAZStoreChar(self.handle, nAddr, 1, int(self.storage_id))
        self.emit_state(ret, f"保存模板(位置{self.storage_id})")


class GetFingerprint2(QRunnable):
    def __init__(self, dll):
        self.signals = WorkerSignals()
        super().__init__()
        self.libc = dll
        self.need_kill = False

    def emit_state(self, code, func_str):
        if code == 0:
            self.signals.step.emit(f"{func_str}成功")
        else:
            self.signals.step.emit(f"{func_str}失败(错误类型/代码：{new_code_dict.get(code)})")

    @Slot()
    def run(self):
        storage_id = c_int(0)
        for i in range(3):
            timeout = 0
            if self.need_kill:
                break
            ret = 40  # 传感器上没有手指
            self.signals.step.emit("请将手指平放在传感器上...")
            while ret != 0 and timeout <= 99:
                # QApplication.processEvents()
                ret = self.libc.GetImage()
                self.signals.step.emit(f"第{timeout + 1}次尝试，{new_code_dict.get(ret)}")
                timeout += 1
            ret = self.libc.GetChar(i)
            self.emit_state(ret, f"生成特征{i + 1}")
            self.signals.step.emit("请抬起手指！")
            QThread.sleep(1)
        ret = self.libc.MergeChar(0, 3)
        self.emit_state(ret, "合并特征")
        ret = self.libc.GetEmptyID(1, 500, byref(storage_id))
        self.emit_state(ret, "获取首个可注册模板位置")
        ret = self.libc.StoreChar(storage_id, 0, 0)
        self.emit_state(ret, f"保存模板(位置{storage_id.value})")

    def kill(self):
        self.need_kill = True


class Terminal(QWidget):
    def __init__(self):
        super().__init__()
        self.thread = None
        # self.timer = QTimer()
        # self.timer.timeout.connect(self.check_midware_status)
        # self.timer.start(3000)
        # UI
        TabWidget.tableWidget.setColumnWidth(0, 160)
        TabWidget.tableWidget.setColumnWidth(1, 60)
        TabWidget.tableWidget.setColumnWidth(2, 60)
        TabWidget.tableWidget.setColumnWidth(3, 70)
        TabWidget.tableWidget.setColumnWidth(4, 70)
        TabWidget.tableWidget.setRowHeight(0, 38)

        TabWidget.listButton.clicked.connect(self.pm2_list)
        TabWidget.reflashButton.clicked.connect(self.check_midware_status)
        TabWidget.startButton.clicked.connect(self.start_mid)
        TabWidget.stopButton.clicked.connect(self.stop_mid)
        TabWidget.restartButton.clicked.connect(self.restart_mid)
        TabWidget.restartdesktopButton.clicked.connect(self.restart_gnome)
        TabWidget.wsButton.clicked.connect(self.ws)
        TabWidget.shButton.clicked.connect(self.open_sh)
        TabWidget.sendButton.clicked.connect(self.send)
        TabWidget.killButton.clicked.connect(self.kill)

    def open_sh(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择Shell脚本", "/nubomed", "Shell脚本 (*.sh)")
        if path:
            TabWidget.textBrowser_2.clear()
            TabWidget.textBrowser_2.setPlainText(f"执行脚本：{path}")
            self.thread = Commander(f"bash {path}")
            self.thread.signals.stdout.connect(TabWidget.textBrowser_2.append)
            threadpool.start(self.thread)

    def promote(self, command):
        if command.__contains__("sudo"):
            command = command.replace("sudo", "sudo -S")
            dialog = QInputDialog()
            dialog.setWindowModality(Qt.WindowModal)
            dialog.setTextEchoMode(QLineEdit.Password)
            dialog.setOkButtonText("确定")
            dialog.setCancelButtonText("取消")
            dialog.setWindowTitle("提升权限")
            dialog.setLabelText("请输入当前用户密码:")
            ok = dialog.exec_()
            password = dialog.textValue()
        else:
            password = None
        return command, password

    def send(self):
        command = TabWidget.lineEdit_2.text()
        command, password = self.promote(command)
        if system == "Windows":
            command = "powershell " + command

        TabWidget.textBrowser_2.clear()
        TabWidget.textBrowser_2.setPlainText(f"执行命令：{command}")
        self.thread = Commander(command, password)
        self.thread.signals.stdout.connect(TabWidget.textBrowser_2.append)
        threadpool.start(self.thread)

    def common_command(self, command, verbose=True):
        command, password = self.promote(command)
        self.thread = Commander(command, password)
        if verbose:
            TabWidget.textBrowser_2.clear()
            TabWidget.textBrowser_2.setPlainText(f"执行命令：{command}")
            self.thread.signals.stdout.connect(TabWidget.textBrowser_2.append)
        else:
            self.thread.signals.verbose.connect(self.parse)
        threadpool.start(self.thread)

    @staticmethod
    def parse(string):
        match = re.search(r"\+---\s(NuboMed\w+Service)\n.*"
                        r"pid\s:\s(\d+)\n.*"
                        r"status\s:\s(\w+)\n.*"
                        r"uptime\s:\s(.+)\n.*"
                        r"memory\susage\s:\s(.+?)\n", string, re.DOTALL)

        if match is not None:
            TabWidget.tableWidget.setItem(0, 0, QTableWidgetItem(match.group(1)))
            TabWidget.tableWidget.setItem(0, 1, QTableWidgetItem(match.group(2)))
            TabWidget.tableWidget.setItem(0, 2, QTableWidgetItem(match.group(3)))
            TabWidget.tableWidget.setItem(0, 3, QTableWidgetItem(match.group(4)))
            TabWidget.tableWidget.setItem(0, 4, QTableWidgetItem(match.group(5)))

    def pm2_list(self):
        self.common_command("pm2 list -m")

    def check_midware_status(self):
        self.common_command("pm2 list -m", verbose=False)
        TabWidget.reflashButton.setEnabled(False)
        QTimer.singleShot(3000, lambda: TabWidget.reflashButton.setEnabled(True))  # 3000毫秒后重新启用按钮，防止快速点击

    def start_mid(self):
        if system == "Windows":
            self.common_command("powershell (net start ConsumableService) -or (net start DrugService)")
        elif system == "Linux":
            json_path, _ = QFileDialog.getOpenFileName(self, "选择Json配置", "/nubomed", "Json配置 (*.json)")
            if path:
                self.common_command(f"bash {path}/shell/pm2_start.sh {json_path}")

    def restart_mid(self):
        self.common_command("pm2 restart 0 -m")

    def stop_mid(self):
        if system == "Windows":
            self.common_command("powershell (net stop ConsumableService) -or (net stop DrugService)")
        elif system == "Linux":
            self.common_command("pm2 stop 0 -m")

    def restart_gnome(self):
        self.common_command("sudo systemctl restart gdm")

    def ws(self):
        dialog = QInputDialog()
        dialog.setWindowModality(Qt.WindowModal)
        dialog.setTextEchoMode(QLineEdit.Normal)
        dialog.setOkButtonText("确定")
        dialog.setCancelButtonText("取消")
        dialog.setWindowTitle("设定端口")
        dialog.setLabelText("请输入WebSocket端口号:")
        dialog.setTextValue("8080")
        ok = dialog.exec_()
        port = dialog.textValue()
        self.common_command(f"wscat -c ws://localhost:{port}/websocket")

    def kill(self):
        # if self.thread.isRunning():
        #     self.thread.requestInterruption()
        #     self.thread.quit()
        #     self.thread.wait()
        # self.thread.deleteLater()
        self.thread.kill()
        TabWidget.textBrowser_2.append("正在终止命令执行...")


class ConfigEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.yaml = YAML()
        self.yaml.preserve_quotes = True
        self.yaml.default_flow_style = False
        self.yaml.indent(mapping=2, sequence=4, offset=2)

        self.cabinet_root_path = "/nubomed/consumable-cabinet-service/conf/"
        self.drug_root_path = "/nubomed/midpkg/drug-middleware/conf/"
        self.browser_cfg_path = "/nubomed/nbrowser/static/localize.json"
        self.device_identify()

        TabWidget.tableWidget_ext.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        TabWidget.tableWidget_2.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        TabWidget.saveButton.clicked.connect(self.save_cfg)
        TabWidget.addlineButton.clicked.connect(self.insert)
        TabWidget.dellineButton.clicked.connect(self.remove)
        TabWidget.checkBox.stateChanged.connect(self.switch)
        # TabWidget.saveButton.setEnabled(False)
        TabWidget.tableWidget_ext.setEnabled(False)
        TabWidget.addButton.clicked.connect(self.add_line)
        TabWidget.delButton.clicked.connect(self.del_line)

        self.read_cfg()

    def device_identify(self):
        # 根据路径判断产品类型，隐藏选项卡
        if os.path.exists(self.cabinet_root_path):
            # 耗材
            self.device_type = 0
            TabWidget.tabWidget.setTabVisible(4, False)
            TabWidget.tabWidget.setTabVisible(5, False)
            TabWidget.tabWidget.setTabVisible(6, False)
            self.sync_cfg_path = self.cabinet_root_path + "application-sync.yml"
            self.nvr_cfg_path = self.cabinet_root_path + "application-nvr.yml"
            self.extern_cfg_path = self.cabinet_root_path + "application-extern.yml"
        elif os.path.exists(self.drug_root_path):
            # 药品
            self.device_type = 1
            TabWidget.tabWidget.setTabVisible(0, False)
            TabWidget.tabWidget.setTabVisible(1, False)
            TabWidget.tabWidget.setTabVisible(2, False)
            self.sync_cfg_path = self.drug_root_path + "application-sync.yml"
            self.nvr_cfg_path = self.drug_root_path + "application-nvr.yml"
            self.extern_cfg_path = self.drug_root_path + "application-extern.yml"
            self.ws_cfg_path = self.drug_root_path + "application-ws.yml"
            self.mcc_cfg_path = self.drug_root_path + "application-mcc.yml"
            self.delay_cfg_path = self.drug_root_path + "application-action-delay.yml"

    @staticmethod
    def insert():
        TabWidget.tableWidget_ext.insertRow(TabWidget.tableWidget_ext.rowCount())

    @staticmethod
    def remove():
        TabWidget.tableWidget_ext.removeRow(TabWidget.tableWidget_ext.currentIndex().row())

    @staticmethod
    def switch(state):
        if state == 2:
            TabWidget.tableWidget_ext.setEnabled(True)
        elif state == 0:
            TabWidget.tableWidget_ext.setEnabled(False)

    @staticmethod
    def add_line():
        TabWidget.tableWidget_2.insertRow(TabWidget.tableWidget_2.rowCount())

    @staticmethod
    def del_line():
        TabWidget.tableWidget_2.removeRow(TabWidget.tableWidget_2.currentIndex().row())

    def read_cfg(self):
        try:
            with open(self.browser_cfg_path, mode='r', encoding="UTF-8") as f:
                self.browser_cfg_dict = json.load(f)
                main_ter_id = self.browser_cfg_dict.get("MAIN_TER_ID")
                main_ter_code = self.browser_cfg_dict.get("MAIN_TER_CODE")
                default_url = self.browser_cfg_dict.get("DefaultURL")
                s_ter_address = self.browser_cfg_dict.get("sTerAddress")
            if self.device_type == 0:
                TabWidget.lineEdit_cfg1.setText(str(main_ter_id))
                TabWidget.lineEdit_cfg2.setText(main_ter_code)
                TabWidget.lineEdit_cfg3.setText(default_url)
                TabWidget.lineEdit_cfg4.setText(s_ter_address)
        except Exception:
            pass

        try:
            with open(self.nvr_cfg_path, mode='r', encoding="UTF-8") as f:
                self.nvr_cfg_dict = self.yaml.load(f)
                enabled = self.nvr_cfg_dict.get("nvr").get("enabled")
                server_ip = self.nvr_cfg_dict.get("nvr").get("device").get("hc-net").get("server-ip")
                username = self.nvr_cfg_dict.get("nvr").get("device").get("hc-net").get("username")
                password = self.nvr_cfg_dict.get("nvr").get("device").get("hc-net").get("password")
                enabled_upload = self.nvr_cfg_dict.get("nvr").get("video").get("enabled-upload")
                upload_save_dir = self.nvr_cfg_dict.get("nvr").get("video").get("upload-save-dir")
                product_channels = self.nvr_cfg_dict.get("nvr").get("device").get("hc-net").get("productChannels")

                TabWidget.tableWidget_2.setRowCount(len(product_channels))
                for idx, child in enumerate(product_channels):
                    item1 = QTableWidgetItem(child.get("productNo"))
                    item1.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                    item2 = QTableWidgetItem(str(child.get("channel")))
                    item2.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                    TabWidget.tableWidget_2.setItem(idx, 0, item1)
                    TabWidget.tableWidget_2.setItem(idx, 1, item2)

                TabWidget.comboBox_2.setCurrentIndex(enabled)
                TabWidget.comboBox_3.setCurrentIndex(enabled_upload)
                TabWidget.lineEdit_5.setText(server_ip)
                my_regex = QRegExp(r'((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})(\.((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})){3}')
                my_validator = QRegExpValidator(my_regex, TabWidget.lineEdit_5)
                TabWidget.lineEdit_5.setValidator(my_validator)
                TabWidget.lineEdit_6.setText(username)
                TabWidget.lineEdit_7.setText(password)
                TabWidget.lineEdit_8.setText(upload_save_dir)
        except Exception:
            pass

        try:
            with open(self.sync_cfg_path, mode='r', encoding="UTF-8") as f:
                self.sync_cfg_dict = self.yaml.load(f)
                host = self.sync_cfg_dict.get("sync").get("server").get("host")
            if self.device_type == 0:
                TabWidget.lineEdit_cfg7.setText(host)
            elif self.device_type == 1:
                regex = QRegExp(r'((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})(\.((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})){3}')
                validator = QRegExpValidator(regex, TabWidget.lineEdit_cfg7_2)
                TabWidget.lineEdit_cfg7_2.setValidator(validator)
                TabWidget.lineEdit_cfg7_2.setText(host)
        except Exception:
            pass

        try:
            with open(self.extern_cfg_path, mode='r', encoding="UTF-8") as f:
                self.extern_cfg_dict = self.yaml.load(f)
                if self.device_type == 0:
                    if self.extern_cfg_dict.get("rodin") is not None:
                        enabled = self.extern_cfg_dict.get("rodin").get("server").get("enabled")
                        TabWidget.checkBox.setChecked(enabled)
                        readers = self.extern_cfg_dict.get("rodin").get("server").get("readers")
                        TabWidget.tableWidget_ext.setRowCount(len(readers))
                        for idx, reader in enumerate(readers):
                            TabWidget.tableWidget_ext.setItem(idx, 0, QTableWidgetItem(reader.get("cabinet-id")))
                            TabWidget.tableWidget_ext.setItem(idx, 1, QTableWidgetItem(reader.get("host")))
                            if reader.get("antennaNos") is not None:
                                TabWidget.tableWidget_ext.setItem(idx, 2, QTableWidgetItem(str(reader.get("antennaNos"))))
                    else:
                        TabWidget.tableWidget_ext.setEnabled(False)
                elif self.device_type == 1:
                    zaz_enabled = self.extern_cfg_dict.get("serial").get("finger").get("zaz").get("enabled")
                    zaz0a0_enabled = self.extern_cfg_dict.get("serial").get("finger").get("zaz0a0").get("enabled")
                    legacy_enabled = self.extern_cfg_dict.get("serial").get("finger").get("legacy").get("enabled")
                    idx = [zaz_enabled, zaz0a0_enabled, legacy_enabled].index(True)
                    baud_no = self.extern_cfg_dict.get("serial").get("finger").get("zaz").get("baud-no")
                    match_threshold = self.extern_cfg_dict.get("serial").get("finger").get("match-threshold")

                    TabWidget.comboBox_4.setCurrentIndex(idx)
                    TabWidget.comboBox_5.setCurrentText(str(baud_no))
                    # TabWidget.lineEdit_9.setValidator(QIntValidator(0, 100))
                    regex = QRegExp(r'^([1-9][0-9]{0,1}|100)$')
                    validator = QRegExpValidator(regex, TabWidget.lineEdit_9)
                    TabWidget.lineEdit_9.setValidator(validator)
                    TabWidget.lineEdit_9.setText(str(match_threshold))
        except Exception:
            pass

        try:
            with open(self.delay_cfg_path, mode='r', encoding="UTF-8") as f:
                self.delay_cfg_dict = self.yaml.load(f)
            if self.device_type == 0:
                pass
            elif self.device_type == 1:
                delay_millis = self.delay_cfg_dict.get("actions").get("delay").get("delay-millis")
                delay_lock = self.delay_cfg_dict.get("actions").get("delay").get("delay-lock")
                time_out_no_lock = self.delay_cfg_dict.get("actions").get("delay").get("time-out-no-lock")

                TabWidget.lineEdit_10.setText(str(delay_millis))
                TabWidget.lineEdit_11.setText(str(delay_lock))
                TabWidget.lineEdit_12.setText(str(time_out_no_lock))
        except Exception:
            pass

        try:
            with open(self.mcc_cfg_path, mode='r', encoding="UTF-8") as f:
                self.mcc_cfg_dict = self.yaml.load(f)
            if self.device_type == 0:
                pass
            elif self.device_type == 1:
                enable = self.mcc_cfg_dict.get("mcc").get("enable")
                host = self.mcc_cfg_dict.get("mcc").get("hub").get("host")

                TabWidget.comboBox_6.setCurrentIndex(enable)
                regex = QRegExp(r'((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})(\.((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})){3}')
                validator = QRegExpValidator(regex, TabWidget.lineEdit_cfg7_4)
                TabWidget.lineEdit_cfg7_4.setValidator(validator)
                TabWidget.lineEdit_cfg7_4.setText(host)
        except Exception:
            pass

        try:
            with open(self.ws_cfg_path, mode='r', encoding="UTF-8") as f:
                self.ws_cfg_dict = self.yaml.load(f)
            if self.device_type == 0:
                pass
            elif self.device_type == 1:
                restructure = self.ws_cfg_dict.get("protocol").get("restructure")
                TabWidget.comboBox_7.setCurrentIndex(restructure)
        except Exception:
            pass

    def save_cfg(self):
        try:
            with open(self.browser_cfg_path, mode='w', encoding="UTF-8") as f:
                if self.device_type == 0:
                    if TabWidget.lineEdit_cfg1.text():
                        self.browser_cfg_dict["MAIN_TER_ID"] = TabWidget.lineEdit_cfg1.text()
                    if TabWidget.lineEdit_cfg2.text():
                        self.browser_cfg_dict["MAIN_TER_CODE"] = TabWidget.lineEdit_cfg2.text()
                    if TabWidget.lineEdit_cfg3.text():
                        self.browser_cfg_dict["DefaultURL"] = TabWidget.lineEdit_cfg3.text()
                    if TabWidget.lineEdit_cfg4.text():
                        self.browser_cfg_dict["sTerAddress"] = TabWidget.lineEdit_cfg4.text()
                json.dump(self.browser_cfg_dict, f, ensure_ascii=False, indent=4)
            TabWidget.label_status.setText("保存成功！")
        except Exception as err:
            TabWidget.label_status.setText(f"保存失败！{err}")

        try:
            with open(self.nvr_cfg_path, mode='w', encoding="UTF-8") as f:
                if self.device_type == 0:
                    if TabWidget.lineEdit_cfg5.text():
                        self.nvr_cfg_dict["nvr"]["nvrIp"] = TabWidget.lineEdit_cfg5.text()
                    if TabWidget.lineEdit_cfg6.text():
                        self.nvr_cfg_dict["nvr"]["reader"][0]["productNo"] = TabWidget.lineEdit_cfg6.text()
                    if TabWidget.lineEdit_cfg7_3.text():
                        self.nvr_cfg_dict["nvr"]["terminale-id"] = TabWidget.lineEdit_cfg7_3.text()
                    if TabWidget.lineEdit_cfg8.text():
                        self.nvr_cfg_dict["nvr"]["mcc"]["server-ip"] = TabWidget.lineEdit_cfg8.text()
                elif self.device_type == 1:
                    self.nvr_cfg_dict["nvr"]["enabled"] = bool(TabWidget.comboBox_2.currentIndex())
                    if TabWidget.lineEdit_5.text():
                        self.nvr_cfg_dict["nvr"]["device"]["hc-net"]["server-ip"] = TabWidget.lineEdit_5.text()
                    if TabWidget.lineEdit_6.text():
                        self.nvr_cfg_dict["nvr"]["device"]["hc-net"]["username"] = TabWidget.lineEdit_6.text()
                    if TabWidget.lineEdit_7.text():
                        self.nvr_cfg_dict["nvr"]["device"]["hc-net"]["password"] = TabWidget.lineEdit_7.text()
                    self.nvr_cfg_dict["nvr"]["video"]["enabled-upload"] = bool(TabWidget.comboBox_3.currentIndex())
                    if TabWidget.lineEdit_8.text():
                        self.nvr_cfg_dict["nvr"]["video"]["upload-save-dir"] = TabWidget.lineEdit_8.text()
                    product_channels = []
                    for i in range(TabWidget.tableWidget_2.rowCount()):
                        product_no = TabWidget.tableWidget_2.item(i, 0).text()
                        channel = TabWidget.tableWidget_2.item(i, 1).text()
                        if product_no and channel:
                            product_channels.append({"productNo": product_no, "channel": int(channel)})
                    self.nvr_cfg_dict["nvr"]["device"]["hc-net"]["productChannels"] = product_channels
                self.yaml.dump(self.nvr_cfg_dict, f)
            TabWidget.label_status.setText("保存成功！")
        except Exception as err:
            TabWidget.label_status.setText(f"保存失败！{err}")

        try:
            with open(self.sync_cfg_path, mode='w', encoding="UTF-8") as f:
                if self.device_type == 0:
                    if TabWidget.lineEdit_cfg7.text():
                        self.sync_cfg_dict["sync"]["server"]["host"] = TabWidget.lineEdit_cfg7.text()
                elif self.device_type == 1:
                    if TabWidget.lineEdit_cfg7_2.text():
                        self.sync_cfg_dict["sync"]["server"]["host"] = TabWidget.lineEdit_cfg7_2.text()
                self.yaml.dump(self.sync_cfg_dict, f)
            TabWidget.label_status.setText("保存成功！")
        except Exception as err:
            TabWidget.label_status.setText(f"保存失败！{err}")

        try:
            with open(self.mcc_cfg_path, mode='w', encoding="UTF-8") as f:
                if self.device_type == 0:
                    pass
                elif self.device_type == 1:
                    self.mcc_cfg_dict["mcc"]["enable"] = bool(TabWidget.comboBox_6.currentIndex())
                    if TabWidget.lineEdit_cfg7_4.text():
                        self.mcc_cfg_dict["mcc"]["hub"]["host"] = TabWidget.lineEdit_cfg7_4.text()
                self.yaml.dump(self.mcc_cfg_dict, f)
            TabWidget.label_status.setText("保存成功！")
        except Exception as err:
            TabWidget.label_status.setText(f"保存失败！{err}")

        try:
            with open(self.ws_cfg_path, mode='w', encoding="UTF-8") as f:
                if self.device_type == 0:
                    pass
                elif self.device_type == 1:
                    self.ws_cfg_dict["protocol"]["restructure"] = bool(TabWidget.comboBox_7.currentIndex())
                self.yaml.dump(self.ws_cfg_dict, f)
            TabWidget.label_status.setText("保存成功！")
        except Exception as err:
            TabWidget.label_status.setText(f"保存失败！{err}")

        try:
            with open(self.delay_cfg_path, mode='w', encoding="UTF-8") as f:
                if self.device_type == 0:
                    pass
                elif self.device_type == 1:
                    if TabWidget.lineEdit_10.text():
                        self.delay_cfg_dict["actions"]["delay"]["delay-millis"] = int(TabWidget.lineEdit_10.text())
                    if TabWidget.lineEdit_11.text():
                        self.delay_cfg_dict["actions"]["delay"]["delay-lock"] = int(TabWidget.lineEdit_11.text())
                    if TabWidget.lineEdit_12.text():
                        self.delay_cfg_dict["actions"]["delay"]["time-out-no-lock"] = int(TabWidget.lineEdit_12.text())
                self.yaml.dump(self.delay_cfg_dict, f)
            TabWidget.label_status.setText("保存成功！")
        except Exception as err:
            TabWidget.label_status.setText(f"保存失败！{err}")

        try:
            with open(self.extern_cfg_path, mode='w', encoding="UTF-8") as f:
                if self.device_type == 0:
                    if self.extern_cfg_dict.get("rodin") is not None:
                        self.extern_cfg_dict["rodin"]["server"]["enabled"] = TabWidget.checkBox.isChecked()
                        readers = []
                        for i in range(TabWidget.tableWidget_ext.rowCount()):
                            cabinet_id = TabWidget.tableWidget_ext.item(i, 0).text()
                            host = TabWidget.tableWidget_ext.item(i, 1).text()
                            if TabWidget.tableWidget_ext.item(i, 2) is not None:
                                antenna_nos = eval(TabWidget.tableWidget_ext.item(i, 2).text())
                                readers.append({"antennaNos": antenna_nos, "cabinet-id": cabinet_id, "host": host,
                                                "port": 4001})
                            else:
                                readers.append({"cabinet-id": cabinet_id, "host": host, "port": 4001})
                        self.extern_cfg_dict["rodin"]["server"]["readers"] = readers
                elif self.device_type == 1:
                    if TabWidget.comboBox_4.currentText() == "方形指纹":
                        self.extern_cfg_dict["serial"]["finger"]["zaz"]["enabled"] = True
                        self.extern_cfg_dict["serial"]["finger"]["zaz0a0"]["enabled"] = False
                        self.extern_cfg_dict["serial"]["finger"]["legacy"]["enabled"] = False
                    elif TabWidget.comboBox_4.currentText() == "圆形指纹":
                        self.extern_cfg_dict["serial"]["finger"]["zaz0a0"]["enabled"] = True
                        self.extern_cfg_dict["serial"]["finger"]["zaz"]["enabled"] = False
                        self.extern_cfg_dict["serial"]["finger"]["legacy"]["enabled"] = False
                    elif TabWidget.comboBox_4.currentText() == "光学指纹":
                        self.extern_cfg_dict["serial"]["finger"]["legacy"]["enabled"] = True
                        self.extern_cfg_dict["serial"]["finger"]["zaz"]["enabled"] = False
                        self.extern_cfg_dict["serial"]["finger"]["zaz0a0"]["enabled"] = False
                    self.extern_cfg_dict["serial"]["finger"]["zaz"]["baud-no"] = int(TabWidget.comboBox_5.currentText())
                    if TabWidget.lineEdit_9.text():
                        self.extern_cfg_dict["serial"]["finger"]["match-threshold"] = int(TabWidget.lineEdit_9.text())
                self.yaml.dump(self.extern_cfg_dict, f)
            TabWidget.label_status.setText("保存成功！")
        except Exception as err:
            TabWidget.label_status.setText(f"保存失败！{err}")


class FingerPrint(QWidget):
    def __init__(self):
        super().__init__()
        self.thread = None
        # self.timer = QTimer()
        if system == "Windows":
            self.libc = cdll.LoadLibrary(f'{path}/bin/win/fingerprint/libapit.dll')
        elif system == "Linux":
            self.libc = cdll.LoadLibrary(f'{path}/bin/linux/fingerprint/libapit.so')
        self.handle = c_int64(0)

        TabWidget.pushButton_closeDevice.setEnabled(False)
        TabWidget.pushButton_getFingerprintNum.setEnabled(False)
        TabWidget.pushButton_getfingerprint.setEnabled(False)
        TabWidget.pushButton_searchfp.setEnabled(False)
        TabWidget.pushButton_del.setEnabled(False)
        TabWidget.pushButton_empty.setEnabled(False)
        TabWidget.comboBox_BaudRate.addItems(self.get_baud_rate())
        TabWidget.comboBox_BaudRate.setCurrentText("57600")
        TabWidget.pushButton_refreshPort.clicked.connect(self.get_port)
        TabWidget.pushButton_openDevice.clicked.connect(self.open_device)
        TabWidget.pushButton_closeDevice.clicked.connect(self.close_device)
        TabWidget.pushButton_getFingerprintNum.clicked.connect(self.get_template_num)
        TabWidget.pushButton_getfingerprint.clicked.connect(self.get_image)
        TabWidget.pushButton_searchfp.clicked.connect(self.search_image)
        TabWidget.pushButton_del.clicked.connect(self.del_flash)
        TabWidget.pushButton_empty.clicked.connect(self.clean_flash)
        # self.timer.timeout.connect(self.availability_check)
        # self.timer.start(2000)

    @staticmethod
    def get_port():
        TabWidget.comboBox_portName.clear()
        TabWidget.comboBox_portName.addItems([com.portName() for com in QSerialPortInfo.availablePorts()])

    @staticmethod
    def get_baud_rate():
        return map(str, QSerialPortInfo.standardBaudRates())

    def availability_check(self):
        # FIXME 端口占用检测对动态库无效
        pass

    def open_device(self):
        TabWidget.textBrowser_3.clear()
        port_name = TabWidget.comboBox_portName.currentText()
        baudrate = TabWidget.comboBox_BaudRate.currentText()

        if port_name:
            nDeviceType = 1  # 串口设备
            iCom = int(port_name[-1])  # 串口号 1-16
            iBaud = int(int(baudrate) / 9600)  # (9600*N)bps,其中N=1—12(默认出厂N=6，即57600bps)

            ret = self.libc.ZAZOpenDeviceEx(byref(self.handle), nDeviceType, iCom, iBaud)
            if ret == 0:
                TabWidget.pushButton_openDevice.setEnabled(False)
                TabWidget.pushButton_closeDevice.setEnabled(True)
                TabWidget.pushButton_getFingerprintNum.setEnabled(True)
                TabWidget.pushButton_getfingerprint.setEnabled(True)
                TabWidget.pushButton_searchfp.setEnabled(True)
                TabWidget.pushButton_del.setEnabled(True)
                TabWidget.pushButton_empty.setEnabled(True)
            else:
                QMessageBox.critical(self, "Error", f"设备未正确打开！{ret}")

    def close_device(self):
        ret = self.libc.ZAZCloseDeviceEx(self.handle)
        if ret == 1 or ret == 0:  # Win动态库返回0代表成功
            TabWidget.pushButton_openDevice.setEnabled(True)
            TabWidget.pushButton_closeDevice.setEnabled(False)
            TabWidget.pushButton_getFingerprintNum.setEnabled(False)
            TabWidget.pushButton_getfingerprint.setEnabled(False)
            TabWidget.pushButton_searchfp.setEnabled(False)
            TabWidget.pushButton_del.setEnabled(False)
            TabWidget.pushButton_empty.setEnabled(False)
        else:
            QMessageBox.critical(self, "Error", "设备未正确关闭！")

    def search_image(self):
        TabWidget.textBrowser_3.clear()
        TabWidget.textBrowser_3.append("请将手指平放在传感器上...")
        i = c_int(0)
        score = c_int(0)
        nAddr = c_int(0xffffffff)
        ret = 2  # 传感器上没有手指
        timeout = 0
        while ret == 2 and timeout <= 99:
            QApplication.processEvents()
            TabWidget.textBrowser_3.append(f"获取指纹图像中...第{timeout + 1}次尝试，"
                                           f"返回值：{code_dict.get(ret, self.libc.ZAZErr2Str(ret))}")
            ret = self.libc.ZAZGetImage(self.handle, nAddr)
            timeout += 1
        if timeout == 100:
            TabWidget.textBrowser_3.append("超时！请重新采集")
            # self.close_device()
            return
        if ret == 0:
            TabWidget.textBrowser_3.append("成功获取指纹")
        else:
            TabWidget.textBrowser_3.append("获取指纹失败")
            # self.close_device()
            return

        ret = self.libc.ZAZGenChar(self.handle, nAddr, 1)
        if ret == 0:
            TabWidget.textBrowser_3.append("生成特征成功")
            code = self.libc.ZAZSearch(self.handle, c_int(0xffffffff), 1, 0, 1049, byref(i), byref(score))
            TabWidget.textBrowser_3.append("***如果返回类型/代码为”没搜索到指纹“，且匹配得分为0，则匹配得到的ID不正确，忽略即可***")
            TabWidget.textBrowser_3.append(f"返回类型/代码：{code_dict.get(code, self.libc.ZAZErr2Str(code))}")
            TabWidget.textBrowser_3.append("匹配的ID：未找到" if i.value == 65022 else f"匹配的ID：{str(i.value)}")
            TabWidget.textBrowser_3.append(f"匹配得分：{str(score.value)}")
        else:
            TabWidget.textBrowser_3.append(f"生成特征失败(错误类型/代码：{code_dict.get(ret, self.libc.ZAZErr2Str(ret))})")
            # self.close_device()

    def get_image(self):
        TabWidget.textBrowser_3.clear()
        # storage_id, _ = QInputDialog.getText(self, "设定Flash存放地址", "请输入一个0-1049之间的数字:", QLineEdit.Normal,
        #                                    str(random.randint(0, 1050)))
        dialog = QInputDialog()
        dialog.setWindowModality(Qt.WindowModal)
        dialog.setTextEchoMode(QLineEdit.Normal)
        dialog.setOkButtonText("确定")
        dialog.setCancelButtonText("取消")
        dialog.setWindowTitle("设定Flash存放地址")
        dialog.setLabelText("请输入一个0-1049之间的数字:")
        dialog.setTextValue(str(random.randint(0, 1050)))
        ok = dialog.exec_()
        storage_id = dialog.textValue()
        if storage_id and ok:
            self.thread = GetFingerprint(storage_id, self.libc, self.handle)
            self.thread.signals.step.connect(TabWidget.textBrowser_3.append)
            threadpool.start(self.thread)

    def del_flash(self):
        # storage_id, _ = QInputDialog.getText(self, "删除指定模板", "请输入要删除的模板ID(0-1049的数字):", QLineEdit.Normal, "")
        dialog = QInputDialog()
        dialog.setWindowModality(Qt.WindowModal)
        dialog.setTextEchoMode(QLineEdit.Normal)
        dialog.setOkButtonText("确定")
        dialog.setCancelButtonText("取消")
        dialog.setWindowTitle("删除指定模板")
        dialog.setLabelText("请输入要删除的模板ID(0-1049的数字):")
        ok = dialog.exec_()
        storage_id = dialog.textValue()
        if storage_id and ok:
            ret = self.libc.ZAZDelChar(self.handle, c_int(0xffffffff), int(storage_id), 1)
            TabWidget.textBrowser_3.append(f"模板{storage_id}删除成功" if ret == 0 else f"模板{storage_id}删除失败")

    def clean_flash(self):
        ret = self.libc.ZAZEmpty(self.handle, c_int(0xffffffff))
        TabWidget.textBrowser_3.append("成功清空指纹库" if ret == 0 else "清空指纹库失败")

    def get_template_num(self):
        num = c_int(0)
        ret = self.libc.ZAZTemplateNum(self.handle, c_int(0xffffffff), byref(num))
        # self.thread = General(self.libc.ZAZTemplateNum, self.handle, c_int(0xffffffff), byref(num))
        # self.thread.signals.step.connect(TabWidget.textBrowser_3.append)
        TabWidget.textBrowser_3.append(f"有效模板总数为{num.value}" if ret == 0 else "获取有效模板总数失败")


class FingerPrint2(QWidget):
    def __init__(self):
        self.thread = None
        super().__init__()
        self.libc = cdll.LoadLibrary(f'{path}/bin/linux/fingerprint/lib0a0.so')

        TabWidget.pushButton_closeDevice_3.setEnabled(False)
        TabWidget.pushButton_getfingerprint_2.setEnabled(False)
        TabWidget.pushButton_searchfp_2.setEnabled(False)
        TabWidget.pushButton_del_2.setEnabled(False)
        TabWidget.pushButton_empty_2.setEnabled(False)
        TabWidget.comboBox_BaudRate_3.addItems(self.get_baud_rate())
        TabWidget.comboBox_BaudRate_3.setCurrentText("57600")
        TabWidget.pushButton_refreshPort_3.clicked.connect(self.get_port)
        TabWidget.pushButton_openDevice_3.clicked.connect(self.open_device)
        TabWidget.pushButton_closeDevice_3.clicked.connect(self.close_device)
        TabWidget.pushButton_getfingerprint_2.clicked.connect(self.get_image)
        TabWidget.pushButton_searchfp_2.clicked.connect(self.search_image)
        TabWidget.pushButton_del_2.clicked.connect(self.del_flash)
        TabWidget.pushButton_empty_2.clicked.connect(self.clean_flash)

    @staticmethod
    def get_port():
        TabWidget.comboBox_portName_3.clear()
        TabWidget.comboBox_portName_3.addItems([com.systemLocation() for com in QSerialPortInfo.availablePorts()])

    @staticmethod
    def get_baud_rate():
        return map(str, QSerialPortInfo.standardBaudRates())

    def open_device(self):
        port_name = TabWidget.comboBox_portName_3.currentText()
        baudrate = TabWidget.comboBox_BaudRate_3.currentText()

        self.libc.OpenDevice(bytes(port_name, 'utf-8'), int(baudrate))
        ret = self.libc.TestConection()

        if ret == 0:
            TabWidget.pushButton_openDevice_3.setEnabled(False)
            TabWidget.pushButton_closeDevice_3.setEnabled(True)
            TabWidget.pushButton_getfingerprint_2.setEnabled(True)
            TabWidget.pushButton_searchfp_2.setEnabled(True)
            TabWidget.pushButton_del_2.setEnabled(True)
            TabWidget.pushButton_empty_2.setEnabled(True)
        else:
            QMessageBox.critical(self, "Error", f"设备未正确打开！{ret}")

    def close_device(self):
        self.thread.kill()
        ret = self.libc.CloseDevice()

        if ret == 1:
            TabWidget.pushButton_openDevice_3.setEnabled(True)
            TabWidget.pushButton_closeDevice_3.setEnabled(False)
            TabWidget.pushButton_getfingerprint_2.setEnabled(False)
            TabWidget.pushButton_searchfp_2.setEnabled(False)
            TabWidget.pushButton_del_2.setEnabled(False)
            TabWidget.pushButton_empty_2.setEnabled(False)
        else:
            QMessageBox.critical(self, "Error", "设备未正确关闭！")

    def get_image(self):
        TabWidget.textBrowser_6.clear()
        self.thread = GetFingerprint2(self.libc)
        self.thread.signals.step.connect(TabWidget.textBrowser_6.append)
        threadpool.start(self.thread)

    def search_image(self):
        TabWidget.textBrowser_6.clear()
        TabWidget.textBrowser_6.append("请将手指平放在传感器上...")
        storage_id = c_int(0)
        score = c_int(0)
        ret = 40  # 传感器上没有手指
        while ret != 0:
            QApplication.processEvents()
            ret = self.libc.GetImage()
            TabWidget.textBrowser_6.append(f"{new_code_dict.get(ret)}")
        ret = self.libc.GetChar(0)
        if ret == 0:
            TabWidget.textBrowser_6.append(f"生成特征成功")
            ret = self.libc.SearchChar(0, byref(storage_id), byref(score))
            TabWidget.textBrowser_6.append(f"进行比对(返回类型/代码：{new_code_dict.get(ret)})")
            TabWidget.textBrowser_6.append(f"匹配的模板位置：{storage_id.value}")
            TabWidget.textBrowser_6.append(f"匹配得分：{score.value * 100}")
        else:
            TabWidget.textBrowser_6.append(f"生成特征失败(错误类型/代码：{new_code_dict.get(ret)})")

    def del_flash(self):
        # storage_id, _ = QInputDialog.getText(self, "删除指定模板", "请输入要删除的模板ID(1-500的数字):", QLineEdit.Normal, "")
        dialog = QInputDialog()
        dialog.setWindowModality(Qt.WindowModal)
        dialog.setTextEchoMode(QLineEdit.Normal)
        dialog.setOkButtonText("确定")
        dialog.setCancelButtonText("取消")
        dialog.setWindowTitle("删除指定模板")
        dialog.setLabelText("请输入要删除的模板ID(1-500的数字):")
        ok = dialog.exec_()
        storage_id = dialog.textValue()
        if storage_id and ok:
            ret = self.libc.DelChar(int(storage_id), int(storage_id), 0)
            TabWidget.textBrowser_6.append(f"模板{storage_id}删除成功" if ret == 0 else f"模板{storage_id}删除失败")

    def clean_flash(self):
        ret = self.libc.DelChar(1, 500, 0)
        TabWidget.textBrowser_6.append(f"{new_code_dict.get(ret)}")


class Camera(QWidget):
    def __init__(self):
        super().__init__()
        self.camera = QCamera()
        self.view_finder = QCameraViewfinder()
        self.view_finder_settings = QCameraViewfinderSettings()
        self.is_opened = False

        TabWidget.pushButton_refreshCam.clicked.connect(self.get_cam)
        TabWidget.pushButton_openCam.clicked.connect(self.cam_switch)
        TabWidget.pushButton_capture.clicked.connect(self.capture)
        TabWidget.horizontalLayout_16.addWidget(self.view_finder)

    @staticmethod
    def get_cam():
        TabWidget.comboBox_chooseCam.clear()
        TabWidget.comboBox_chooseCam.addItems([cam_info.deviceName() for cam_info in QCameraInfo.availableCameras()])

    def cam_switch(self):
        for cam_info in QCameraInfo.availableCameras():
            if cam_info.deviceName() == TabWidget.comboBox_chooseCam.currentText():
                self.camera = QCamera(cam_info)
                self.camera.setCaptureMode(QCamera.CaptureViewfinder)

                self.view_finder_settings.setResolution(640, 480)
                self.view_finder_settings.setMaximumFrameRate(30)
                self.camera.setViewfinderSettings(self.view_finder_settings)

                self.camera.setViewfinder(self.view_finder)

                if not self.is_opened:
                    self.camera.start()
                    self.is_opened = True
                    TabWidget.pushButton_openCam.setText(self.tr("关闭摄像头"))
                else:
                    self.camera.stop()
                    self.is_opened = False
                    TabWidget.pushButton_openCam.setText(self.tr("开启摄像头"))

    def capture(self):
        cap = QCameraImageCapture(self.camera)
        cap.setCaptureDestination(QCameraImageCapture.CaptureToFile)
        cap.capture("C:/Users/Nehcknarf/PycharmProjects/midtool/test")
        TabWidget.label_cap.setText(self.tr("拍照成功，存储于工具目录下 test.jpg"))


class Arcsoft(QWidget):
    def __init__(self):
        super().__init__()
        self.thread = None
        # self.yaml = YAML()
        # self.request = QNetworkRequest()
        # self.manager = QNetworkAccessManager()
        # self.manager.finished.connect(self.check_active_slot)

        TabWidget.pushButton_generator.clicked.connect(self.generator)
        # TabWidget.pushButton_checkLicense.clicked.connect(self.check_active)
        TabWidget.pushButton_activateOline.clicked.connect(self.activate)

        # if system == "Linux":
        #     try:
        #         with open("/nubomed/consumable-cabinet-service/conf/application-camera.yml", mode='r', encoding="UTF-8") as f:
        #             self.camera_cfg_dict = self.yaml.load(f)
        #             app_id = self.camera_cfg_dict.get("arcsoft").get("AppId")
        #             sdk_key = self.camera_cfg_dict.get("arcsoft").get("SdkKey")
        #             active_key = self.camera_cfg_dict.get("arcsoft").get("ActiveKey")
        #             TabWidget.lineEdit_appId.setText(app_id)
        #             TabWidget.lineEdit_sdkKey.setText(sdk_key)
        #             TabWidget.lineEdit_activateKey.setText(active_key)
        #     except FileNotFoundError:
        #         TabWidget.textBrowser_arcsoft.append(f"未找到摄像头配置文件 application-camera.yml")

    def generator(self):
        TabWidget.textBrowser_arcsoft.clear()
        # password, ok = QInputDialog.getText(self, "提升权限", "请输入当前账户密码:", QLineEdit.Password, "")
        dialog = QInputDialog()
        dialog.setWindowModality(Qt.WindowModal)
        dialog.setTextEchoMode(QLineEdit.Password)
        dialog.setOkButtonText("确定")
        dialog.setCancelButtonText("取消")
        dialog.setWindowTitle("提升权限")
        dialog.setLabelText("请输入当前账户密码:")
        ok = dialog.exec_()
        password = dialog.textValue()
        if password and ok:
            TabWidget.textBrowser_arcsoft.setPlainText("执行脚本：/nubomed/arcsoft/arcsoftsetup.sh")
            self.thread = Commander(f"bash /nubomed/arcsoft/arcsoftsetup.sh {password}")
            self.thread.signals.stdout.connect(TabWidget.textBrowser_arcsoft.append)
            threadpool.start(self.thread)

    # def check_active(self):
    #     TabWidget.textBrowser_arcsoft.clear()
    #     self.request.setUrl(QUrl("http://localhost:8080/system/getActiveInfo"))
    #     self.manager.get(self.request)
    #
    # @staticmethod
    # def check_active_slot(reply):
    #     if reply.error() == QNetworkReply.NoError:
    #         res = json.loads(reply.readAll().data())
    #         if res.get('activeState') is not None:
    #             TabWidget.textBrowser_arcsoft.append(f"激活状态：{res.get('activeState')}")
    #         if res.get('appId') is not None:
    #             TabWidget.textBrowser_arcsoft.append(f"App ID：{res.get('appId')}")
    #         if res.get('sdkKey') is not None:
    #             TabWidget.textBrowser_arcsoft.append(f"SDK Key：{res.get('sdkKey')}")
    #         if res.get('activeKey') is not None:
    #             TabWidget.textBrowser_arcsoft.append(f"激活密钥：{res.get('activeKey')}")
    #     else:
    #         TabWidget.textBrowser_arcsoft.append(reply.errorString())

    def activate(self):
        TabWidget.textBrowser_arcsoft.clear()
        active_key = TabWidget.lineEdit_activateKey.text()

        # query = QUrlQuery()
        # query.addQueryItem("AppId", app_id)
        # query.addQueryItem("SdkKey", sdk_key)
        # query.addQueryItem("activeKey", active_key)
        #
        # url = QUrl("http://localhost:8080/system/activeFaceEngin?")
        # url.setQuery(query.query())
        #
        # self.request.setUrl(url)
        # self.manager.get(self.request)

        if active_key:
            self.thread = Commander(f"bash arsoft_Active.sh F3sE2YzxMYy4VAFCRiLCz9NzBmQeCMB8nN2fVyo7F4Ca 8bLYHqy1QaCzqbQ5PrDuQFGfmk1QJneYV216uSjDBq7v {active_key}", wd="/nubomed/midtool/shell/")
            # 测试环境
            # self.thread = Commander(
            #     f"bash {path}/shell/arsoft_Active.sh DEF4Zavuu24UjseJgrYGaGbyHD8C7MZBbDimLN3joSmE 3sfW9ijmvQqUNCvBrNgJNzWxT7rCsfaxDsyU7XzQKA4Q {active_key}")
            self.thread.signals.stdout.connect(TabWidget.textBrowser_arcsoft.append)
            threadpool.start(self.thread)


class Scan(QWidget):
    def __init__(self):
        super().__init__()
        self.ser = QSerialPort()
        self.ser.readyRead.connect(self.read)
        self.thread = Serial(self.ser)
        self.thread.signals.pinout.connect(TabWidget.textBrowser_4.append)

        TabWidget.pushButton_refreshPort_2.clicked.connect(self.get_port)
        TabWidget.comboBox_BaudRate_2.addItems(self.get_baud_rate())
        TabWidget.comboBox_BaudRate_2.setCurrentText("115200")
        TabWidget.pushButton_openDevice_2.clicked.connect(self.open)
        TabWidget.pushButton_closeDevice_2.setEnabled(False)
        TabWidget.pushButton_closeDevice_2.clicked.connect(self.close)
        TabWidget.pushButton_cls.clicked.connect(self.cls)

    @staticmethod
    def get_port():
        TabWidget.comboBox_portName_2.clear()
        TabWidget.comboBox_portName_2.addItems([com.portName() for com in QSerialPortInfo.availablePorts()])

    @staticmethod
    def get_baud_rate():
        return map(str, QSerialPortInfo.standardBaudRates())

    def open(self):
        if self.ser.isOpen():
            return
        else:
            TabWidget.textBrowser_4.clear()
            port_name = TabWidget.comboBox_portName_2.currentText()
            baud_rate = TabWidget.comboBox_BaudRate_2.currentText()

            self.ser.setPortName(port_name)
            self.ser.setBaudRate(int(baud_rate))
            # self.ser.setReadBufferSize(0)
            ret = self.ser.open(QIODevice.ReadOnly)
            if ret:
                TabWidget.pushButton_openDevice_2.setEnabled(False)
                TabWidget.pushButton_closeDevice_2.setEnabled(True)
                TabWidget.textBrowser_4.append("串口打开成功")
            else:
                TabWidget.textBrowser_4.append("串口打开失败")

    def read(self):
        self.thread.run()
        # TODO 关注
        # threadpool.start(self.thread)

    def close(self):
        if self.ser.isOpen():
            self.ser.close()
        TabWidget.textBrowser_4.append("设备已关闭")
        TabWidget.pushButton_openDevice_2.setEnabled(True)
        TabWidget.pushButton_closeDevice_2.setEnabled(False)

    @staticmethod
    def cls():
        TabWidget.textBrowser_4.clear()


class MidUpgrade(QWidget):
    def __init__(self):
        super().__init__()
        self.thread = None
        self.device_type = -1
        self.pkg_path = None

        TabWidget.buttonGroup.idClicked.connect(self.get_device_type)
        TabWidget.installButton.clicked.connect(self.install)
        TabWidget.chooseButton.clicked.connect(self.choose_upgrade_pkg)
        TabWidget.upgradeButton.clicked.connect(self.upgrade)

    def get_device_type(self, btn_id):
        self.device_type = abs(btn_id) - 1
        # print(self.device_type)

    def install(self):
        wd_path = glob.glob("/nubomed/consumable-cabinet-service_V*/")[0]
        if self.device_type > 0:
            self.thread = Commander(f"bash install.sh {self.device_type}", wd=wd_path)
            self.thread.signals.stdout.connect(TabWidget.textBrowser_5.append)
            threadpool.start(self.thread)
        else:
            TabWidget.textBrowser_5.append("请先选择柜子类型！再点击安装")

    def choose_upgrade_pkg(self):
        self.pkg_path, _ = QFileDialog.getOpenFileName(self, "选择升级包", "/media", "升级包 (*.tar.gz)")
        if self.pkg_path:
            TabWidget.textBrowser_5.clear()
            TabWidget.textBrowser_5.append(f"选中的升级包所在路径：{self.pkg_path}")

    def upgrade(self):
        if self.pkg_path:
            self.thread = Commander(f"bash {path}/shell/upgrade_version.sh {self.pkg_path}")
            self.thread.signals.stdout.connect(TabWidget.textBrowser_5.append)
            threadpool.start(self.thread)


if __name__ == "__main__":
    QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    system = platform.system()
    app = QApplication(sys.argv)
    translator = QTranslator(app)
    if QLocale.system().name() == "zh_TW":
        translator.load(':/i18n/lang/zh_TW.qm')
        app.installTranslator(translator)
    # app.setStyle('Fusion')
    serverName = 'MidTool'
    socket = QLocalSocket()
    socket.connectToServer(serverName)
    if socket.waitForConnected(500):
        app.quit()
    else:
        localServer = QLocalServer()
        localServer.listen(serverName)

        loader = QUiLoader()
        TabWidget = loader.load(':/ui/midtool.ui')
        TabWidget.setWindowIcon(QIcon(':/icon/bin/icon/icon.png'))
        # 使窗口显示在屏幕中心
        center = QGuiApplication.primaryScreen().availableGeometry().center()  # 获取屏幕的中心点
        geometry = TabWidget.geometry()
        geometry.moveCenter(center)
        TabWidget.setGeometry(geometry)

        # 多系统兼容
        if system == "Windows":
            # system_tray_icon = QSystemTrayIcon()
            # system_tray_icon.setIcon(QIcon(f'{path}/icon.png'))
            # system_tray_icon.show()
            # 关闭部分不支持的功能的标签/按钮
            TabWidget.setTabVisible(1, False)  # 部署升级 Tab
            TabWidget.setTabVisible(2, False)  # 配置文件修改 Tab
            TabWidget.setTabVisible(6, False)  # 人脸识别 Tab
            # TODO 更新win监控功能
            TabWidget.tabWidget_2.setTabVisible(1, False)  # 圆形指纹 Tab
            TabWidget.reflashButton.setEnabled(False)
            TabWidget.listButton.setEnabled(False)
            TabWidget.restartButton.setEnabled(False)
            TabWidget.restartdesktopButton.setEnabled(False)
            TabWidget.wsButton.setEnabled(False)
            TabWidget.shButton.setEnabled(False)
            TabWidget.StartDateEdit.setEnabled(False)
            TabWidget.EndDateEdit.setEnabled(False)
            TabWidget.downlogButton.setEnabled(False)
        elif system == "Linux":
            # 高分屏缩放
            # os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
            os.environ["QT_SCALE_FACTOR"] = "1.25"
            # Ubuntu 22.04
            # os.environ["QT_QPA_PLATFORM"] = "wayland"
            # Ubuntu 20.04
            os.environ["QT_QPA_PLATFORM"] = "xcb"
            if os.path.exists("/nubomed/midpkg/drug-middleware/"):
                TabWidget.setTabVisible(0, False)  # 药柜关闭进程管理 Tab
            fp2 = FingerPrint2()
        # 外部传参支持
        parser = QCommandLineParser()
        tab = QCommandLineOption(["t", "tab"], "Choice which tab to be shown at start up", "tab")
        parser.addOption(tab)
        parser.process(app)
        tab = parser.value(tab)
        # Nbtool传参选择启动标签页（参数：标签页currentIndex）
        tab_idx_list = [0, 1, 2, 3, 4, 5, 6, 12]
        tab_dict = {"face": 6, "camera": 5, "fingerprint": 4, "serial_device": 3}
        if tab:
            index = tab_dict.get(tab)
            tab_idx_list.remove(index)
            for i in tab_idx_list:
                TabWidget.setTabVisible(i, False)
            TabWidget.setCurrentIndex(index)

        ter = Terminal()
        cfg = ConfigEditor()
        fp = FingerPrint()
        cam = Camera()
        arc = Arcsoft()
        scan = Scan()
        mu = MidUpgrade()
        # 置顶
        TabWidget.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.WindowCloseButtonHint)
        TabWidget.activateWindow()
        TabWidget.raise_()
        TabWidget.show()

        sys.exit(app.exec_())

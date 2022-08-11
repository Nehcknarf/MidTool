import os
import sys
import re
import random
import logging
import struct
from collections import deque
from ctypes import *
from datetime import datetime

import PySide2.QtQuick
from PySide2.QtMultimedia import QCameraInfo, QCamera, QCameraViewfinderSettings, QCameraImageCapture
from PySide2.QtMultimediaWidgets import QCameraViewfinder
# from PySide2.QtNetwork import QNetworkRequest, QNetworkAccessManager, QHttpMultiPart, QHttpPart, QNetworkReply
from PySide2.QtNetwork import QLocalSocket, QLocalServer
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication, QWidget, QFileDialog, QInputDialog, QMessageBox, QLineEdit, \
    QFileSystemModel, QTableWidgetItem
from PySide2.QtCore import Qt, QThread, Signal, QDir, QFile, QIODevice, QTextStream, QRegExp, QProcess, QSize, \
    QModelIndex, QCoreApplication  # QTimer, QUrl, QByteArray, QJsonDocument, QEventLoop
from PySide2.QtGui import QTextCursor, QTextCharFormat, QColor
from PySide2.QtSerialPort import QSerialPortInfo, QSerialPort

# Ubuntu 22.04
# os.environ["QT_QPA_PLATFORM"] = "wayland"
# Ubuntu 20.04
os.environ["QT_QPA_PLATFORM"] = "xcb"
# DEBUG
# os.environ["QT_DEBUG_PLUGINS"] = "1"
# 虚拟键盘
os.environ["QT_IM_MODULE"] = "qtvirtualkeyboard"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(level=logging.WARN)

# 指昂指纹模块返回码字典
code_dict = {0: "执行成功", 1: "数据包接收错误", 2: "传感器上没有手指", 3: "录入指纹图象失败", 4: "指纹太淡", 5: "指纹太糊",
             6: "指纹太乱", 7: "指纹特征点太少", 8: "指纹不匹配", 9: "没搜索到指纹", 10: "特征合并失败", 11: "地址号超出指纹库范围",
             12: "从指纹库读模板出错", 13: "上传特征失败", 14: "模块不能接收后续数据包", 15: "上传图象失败", 16: "删除模板失败",
             17: "清空指纹库失败", 18: "不能进入休眠", 19: "口令不正确", 20: "系统复位失败", 21: "无效指纹图象"}

device_dict = {"0708": "身份RFID读卡器类", "0107": "条码扫描头类", }


class Commander(QThread):
    stdout = Signal(str)
    verbose = Signal(str)

    def __init__(self, command, password=None):
        super().__init__()
        self.command = command
        self.password = password

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

        process_command.setWorkingDirectory("/nubomed")
        process_command.setProgram(self.command.split()[0])
        process_command.setArguments(self.command.split()[1:])
        process_command.start()
        # process_command.start(self.command)
        process_command.waitForStarted()
        string = ""
        while process_command.state() != QProcess.NotRunning:
            QApplication.processEvents()
            if QThread.currentThread().isInterruptionRequested():
                break
            if process_command.waitForReadyRead():
                stdout = bytes(process_command.readAllStandardOutput()).decode("utf8").rstrip('\n')
                self.stdout.emit(stdout)
                string += f"{stdout}\n"

        self.verbose.emit(string)
        self.stdout.emit("指令已执行")


class Reader(QThread):
    context = Signal(str)

    def __init__(self, path, chunk=524288):  # 512KB
        super().__init__()
        self.path = path
        self.chunk = chunk

    def run(self):
        file = QFile(self.path)
        if not file.open(QIODevice.ReadOnly | QIODevice.Text):
            return
        file.seek(file.size() - self.chunk)
        # while not file.atEnd():
        #     QApplication.processEvents()
        # mem = file.map(-1, self.pos)
        # file.unmap(mem)
        log = bytes(file.readAll()).decode('utf8')
        self.context.emit(log)
        file.close()


class Searcher(QThread):
    match = Signal(str)

    def __init__(self, keyword, text, match_case, cursor):
        super().__init__()
        self.q = deque()
        self.keyword = keyword
        self.text = text
        self.match_case = match_case
        self.rx = QRegExp(self.keyword, self.match_case)

    def run(self):
        pass


class Serial(QThread):
    pinout = Signal(str)

    def __init__(self, ser):
        super().__init__()
        self.ser = ser
        self.total_data = b''

    def run(self):
        if self.ser.bytesAvailable():
            bytes_data = self.ser.readAll().data()  # bytes
            self.total_data += bytes_data
            print(self.total_data)
            if re.findall(b'~.*\xe7', self.total_data):
                try:
                    header_tuple = struct.unpack("<chc4s4s2h2scB2s2ch", self.total_data[:26])
                except struct.error as err:
                    data = f"数据头解析失败，{err}"
                    self.total_data = self.total_data[1:]
                else:
                    header_list = [i.hex() if isinstance(i, bytes) else i for i in header_tuple]
                    device_type = header_list[10]
                    payload_length = header_list[-1]
                    try:
                        payload_tuple = struct.unpack("13B", self.total_data[26:26+payload_length])
                        # ending_tuple = struct.unpack("2sc", self.total_data[26 + payload_length:29 + payload_length])
                    except struct.error as err:
                        data = f"数据载荷/尾解析失败，{err}"
                    else:
                        self.total_data = self.total_data[29 + payload_length + 6:]
                        # ending_list = [i.hex() for i in ending_tuple]
                        # data = tuple(header_list) + payload_tuple + tuple(ending_list)
                        # print(data)
                        if device_type == "0708":
                            card_type = payload_tuple[0]
                            card_uid = "-".join(map(str, payload_tuple[1:]))
                            data = f"设备类型：{device_dict.get(device_type)}，卡类型：{card_type}，卡号：{card_uid}"
                        elif device_type == "0108":
                            pass
                finally:
                    self.pinout.emit(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')}，{data}")


class GetFingerprint(QThread):
    step = Signal(str)

    def __init__(self, store_id, dll, handle):
        super().__init__()
        self.store_id = store_id
        self.libc = dll
        self.handle = handle

    def emit_state(self, code, func_str):
        if code == 0:
            self.step.emit(f"{func_str}成功")
        else:
            self.step.emit(f"{func_str}失败(错误类型/代码：{code_dict.get(code, self.libc.ZAZErr2Str(code))})")
            return

    def run(self):
        nAddr = c_int(0xffffffff)
        self.step.emit("请将手指平放在传感器上...")
        ret = 2  # 传感器上没有手指
        timeout = 0
        while ret == 2 and timeout <= 99:
            QApplication.processEvents()
            self.step.emit(f"获取指纹图像中...第{timeout + 1}次尝试，返回值：{code_dict.get(ret, self.libc.ZAZErr2Str(ret))}")
            ret = self.libc.ZAZGetImage(self.handle, nAddr)
            timeout += 1
        if timeout == 100:
            self.step.emit("超时！请重新采集")
            return
        self.emit_state(ret, "第一次采集指纹")

        ret = self.libc.ZAZGenChar(self.handle, nAddr, 2)
        self.emit_state(ret, "生成特征A")

        self.step.emit("请抬起手指！")
        QThread.sleep(1)
        self.step.emit("请再次将手指平放在传感器上...")

        ret = 2  # 传感器上没有手指
        timeout = 0
        while ret == 2 and timeout <= 99:
            QApplication.processEvents()
            self.step.emit(f"获取指纹图像中...第{timeout + 1}次尝试，返回值：{code_dict.get(ret, self.libc.ZAZErr2Str(ret))}")
            ret = self.libc.ZAZGetImage(self.handle, nAddr)
            timeout += 1
        if timeout == 100:
            self.step.emit("超时！请重新采集")
            return
        self.emit_state(ret, "第二次采集指纹")

        ret = self.libc.ZAZGenChar(self.handle, nAddr, 1)
        self.emit_state(ret, "生成特征B")

        ret = self.libc.ZAZRegModule(self.handle, nAddr)
        self.emit_state(ret, "合并特征")

        ret = self.libc.ZAZStoreChar(self.handle, nAddr, 1, int(self.store_id))
        self.emit_state(ret, f"保存模板(位置{self.store_id})")


class LogBrowser(QWidget):
    def __init__(self):
        super().__init__()
        self.q = deque()
        self.keyword_len = 0
        self.thread = QThread()
        self.thread_read = QThread()
        # self.thread_search = QThread()
        # UI
        TabWidget.textBrowser.ensureCursorVisible()
        TabWidget.textBrowser.document().setMaximumBlockCount(5000)

        TabWidget.openfileButton.clicked.connect(self.open_log)
        TabWidget.tailButton.clicked.connect(self.tail_log)
        TabWidget.stoptailButton.clicked.connect(self.kill_tail)
        TabWidget.clearButton.clicked.connect(TabWidget.lineEdit.clear)
        TabWidget.searchButton.clicked.connect(self.search)
        TabWidget.prevButton.clicked.connect(self.prev)
        TabWidget.nextButton.clicked.connect(self.next)
        # TabWidget.lineEdit.textChanged.connect(self.search)
        TabWidget.match_case.stateChanged.connect(self.search)
        TabWidget.match_word.stateChanged.connect(self.search)
        # TabWidget.textBrowser.verticalScrollBar().valueChanged.connect(self.auto_load)

    def auto_load(self):
        v_value = TabWidget.textBrowser.verticalScrollBar().value()
        if v_value < 100:
            TabWidget.textBrowser.moveCursor(QTextCursor.Start)
            # TabWidget.textBrowser.insertPlainText("test")

    def open_log(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择日志文件", TabWidget.logpathlineEdit.text(), "日志文件 (*.log)")
        if path:
            TabWidget.textBrowser.clear()
            self.thread_read = Reader(path)
            self.thread_read.context.connect(TabWidget.textBrowser.append, Qt.BlockingQueuedConnection)
            # self.thread_read.context.connect(TabWidget.textBrowser.setText)
            self.thread_read.start()

    def tail_log(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择待监控的日志文件", TabWidget.logpathlineEdit.text(), "日志文件 (*.log)")
        if path:
            TabWidget.textBrowser.clear()
            self.thread = Commander(f"tail -f -n 30 {path}")
            self.thread.stdout.connect(TabWidget.textBrowser.append)
            self.thread.start()

    def kill_tail(self):
        if self.thread.isRunning():
            self.thread.requestInterruption()
            self.thread.quit()
            self.thread.wait()
        self.thread.deleteLater()
        TabWidget.textBrowser.append("终止命令执行成功，线程释放")

    def highlight(self, pos):
        cursor = TabWidget.textBrowser.textCursor()
        cursor.setPosition(pos)
        cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, self.keyword_len)
        # Set the visible cursor
        TabWidget.textBrowser.setTextCursor(cursor)

    def prev(self):
        pos = self.q.pop()
        self.q.appendleft(pos)
        self.highlight(pos)

    def next(self):
        pos = self.q.popleft()
        self.q.append(pos)
        self.highlight(pos)

    def search(self):
        keyword = TabWidget.lineEdit.text()
        self.keyword_len = len(keyword)
        if not keyword:
            return
        context = TabWidget.textBrowser.toPlainText()
        # 恢复默认的颜色
        cursor = TabWidget.textBrowser.textCursor()
        cursor.select(QTextCursor.Document)
        cursor.setCharFormat(QTextCharFormat())
        cursor.clearSelection()
        TabWidget.textBrowser.setTextCursor(cursor)
        TabWidget.textBrowser.moveCursor(QTextCursor.Start)

        fmt = QTextCharFormat()
        fmt.setBackground(QColor.fromRgbF(1.000000, 1.000000, 0.000000, 1.000000))

        if TabWidget.match_case.isChecked():
            match_case = Qt.CaseSensitive
        else:
            match_case = Qt.CaseInsensitive

        if TabWidget.match_word.isChecked():
            keyword = f"\\b{keyword}\\b"

        self.q.clear()
        # Returns the position of the first match, or -1 if there was no match.
        rx = QRegExp(keyword, match_case)
        pos = rx.indexIn(context, 0)
        if pos != -1:
            self.q.append(pos)
        while pos != -1:
            QApplication.processEvents()
            cursor.setPosition(pos)
            cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, self.keyword_len)
            cursor.mergeCharFormat(fmt)
            pos += rx.matchedLength()
            pos = rx.indexIn(context, pos)
            if pos != -1:
                self.q.append(pos)

        TabWidget.label.setText(f"找到{len(self.q)}处")


class Terminal(QWidget):
    def __init__(self):
        super().__init__()
        self.thread = QThread()
        self.thread_cc = QThread()
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
            self.thread = Commander(f"/bin/sh {path}")
            self.thread.stdout.connect(TabWidget.textBrowser_2.append)
            self.thread.start()

    def promote(self, command):
        if command.__contains__("sudo"):
            command = command.replace("sudo", "sudo -S")
            password, _ = QInputDialog.getText(self, "提升权限", "请输入Root密码:", QLineEdit.Normal, "")
        else:
            password = None
        return command, password

    def send(self):
        command = TabWidget.lineEdit_2.text()
        command, password = self.promote(command)

        TabWidget.textBrowser_2.clear()
        TabWidget.textBrowser_2.setPlainText(f"执行命令：{command}")
        self.thread = Commander(command, password)
        self.thread.stdout.connect(TabWidget.textBrowser_2.append)
        self.thread.start()

    def common_command(self, command, verbose=True):
        command, password = self.promote(command)
        self.thread_cc = Commander(command, password)
        if verbose:
            TabWidget.textBrowser_2.clear()
            TabWidget.textBrowser_2.setPlainText(f"执行命令：{command}")
            self.thread_cc.stdout.connect(TabWidget.textBrowser_2.append)
        else:
            self.thread_cc.verbose.connect(self.parse)
        self.thread_cc.start()

    @staticmethod
    def parse(string):
        match = re.search(r"\+---\s(NuboMedCollateService)\n.*"
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

    def start_mid(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择Json配置", "/nubomed", "Json配置 (*.json)")
        if path:
            self.common_command(f"pm2 start {path} -m")

    def restart_mid(self):
        self.common_command("pm2 restart 0 -m")

    def stop_mid(self):
        self.common_command("pm2 stop 0 -m")

    def restart_gnome(self):
        self.common_command("sudo systemctl restart gdm")

    def ws(self):
        port, _ = QInputDialog.getText(self, "设定端口", "请输入WebSocket端口号:", QLineEdit.Normal, "")
        if port:
            self.common_command(f"wscat -c ws://localhost:{port}")

    def kill(self):
        if self.thread.isRunning():
            self.thread.requestInterruption()
            self.thread.quit()
            self.thread.wait()
        self.thread.deleteLater()
        TabWidget.textBrowser_2.append("终止命令执行成功，线程释放")


class YamlConfig(QWidget):
    def __init__(self):
        super().__init__()
        self.path = "/"
        self.file_name = ""

        TabWidget.opencfgdirButton.clicked.connect(self.open_dir)
        TabWidget.comboBox.currentIndexChanged.connect(self.open_cfg)
        TabWidget.saveButton.clicked.connect(self.save)
        TabWidget.saveasButton.clicked.connect(self.save_as)

    def open_dir(self):
        TabWidget.comboBox.clear()
        path = TabWidget.cfgpathlineEdit.text()
        self.path = QFileDialog.getExistingDirectory(self, "请选择配置文件所在的文件夹", path, QFileDialog.DontResolveSymlinks)
        if self.path:
            cfg_dir = QDir(self.path)
            cfg_dir.setNameFilters(["*.yml"])
            cfg_list = cfg_dir.entryInfoList()
            TabWidget.comboBox.addItems([i.fileName() for i in cfg_list])

    def open_cfg(self):
        self.file_name = TabWidget.comboBox.currentText()
        file = QFile(f"{self.path}/{self.file_name}")
        if not file.open(QIODevice.ReadOnly | QIODevice.Text):
            return
        content = QTextStream(file)
        content.setAutoDetectUnicode(True)
        content = content.readAll()
        TabWidget.plainTextEdit.setPlainText(content)
        file.close()

    def save(self):
        with open(f"{self.path}/{self.file_name}", 'w', encoding='utf-8') as f:
            content = TabWidget.plainTextEdit.toPlainText()
            f.write(content)

    def save_as(self):
        filename, _ = QFileDialog.getSaveFileName(self, "保存配置", "/nubomed", "Yaml文件 (*.yml)")
        with open(f"{filename}.yml", 'w', encoding='utf-8') as f:
            content = TabWidget.plainTextEdit.toPlainText()
            f.write(content)


class FileManager(QWidget):
    def __init__(self):
        super().__init__()
        self.model_index = QModelIndex()
        self.model = QFileSystemModel()
        self.model.setRootPath("/media")
        self.model.setReadOnly(False)

        TabWidget.treeView.setModel(self.model)
        TabWidget.treeView.setRootIndex(self.model.index("/nubomed"))
        TabWidget.treeView.setColumnWidth(0, 200)
        TabWidget.treeView.setIconSize(QSize(30, 30))

        TabWidget.treeView_driver.setModel(self.model)
        TabWidget.treeView_driver.setRootIndex(self.model.index("/media"))
        TabWidget.treeView_driver.setColumnWidth(0, 200)
        TabWidget.treeView_driver.setIconSize(QSize(30, 30))

        TabWidget.treeView.clicked.connect(self.left)
        TabWidget.treeView_driver.clicked.connect(self.right)
        TabWidget.pushButton_open.clicked.connect(self.open)
        TabWidget.pushButton_mkdir.clicked.connect(self.mkdir)
        TabWidget.pushButton_remove.clicked.connect(self.rm)
        # TabWidget.pushButton_copy.clicked.connect()

    def left(self, index):
        TabWidget.treeView_driver.clearSelection()
        self.path = self.model.filePath(index)

    def right(self, index):
        TabWidget.treeView.clearSelection()
        self.path = self.model.filePath(index)

    def popup(self):
        msg_box = QMessageBox()
        msg_box.setWindowTitle("错误")
        msg_box.setText("文件已经存在")
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.exec()

    def open(self):
        path = QFileDialog.getExistingDirectory(self, "打开文件夹", "/home", QFileDialog.ShowDirsOnly)
        if path:
            TabWidget.treeView.setRootIndex(self.model.index(path))

    def mkdir(self):
        dir_name, _ = QInputDialog.getText(self, "新建文件夹", "请输入文件夹名称", QLineEdit.Normal, "")
        if dir_name:
            self.model.mkdir(self.model_index.parent(), dir_name)

    def rm(self):
        self.model.remove(self.model_index)


class FingerPrint(QWidget):
    def __init__(self):
        super().__init__()
        # self.timer = QTimer()
        # 本地测试
        # self.libc = cdll.LoadLibrary("./libapit.so")
        # 生产环境
        self.libc = cdll.LoadLibrary("/nubomed/midtool/libapit.so")
        self.handle = c_int(0)

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
        if ret == 1:
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
            code = self.libc.ZAZSearch(self.handle, c_int(0xffffffff), 1, 0, 9999, byref(i), byref(score))
            TabWidget.textBrowser_3.append("***如果返回类型/代码为”没搜索到指纹“，且匹配得分为0，则匹配得到的ID不正确，忽略即可***")
            TabWidget.textBrowser_3.append(f"返回类型/代码：{code_dict.get(code, self.libc.ZAZErr2Str(code))}")
            TabWidget.textBrowser_3.append("匹配的ID：未找到" if i.value == 65022 else f"匹配的ID：{str(i.value)}")
            TabWidget.textBrowser_3.append(f"匹配得分：{str(score.value)}")
        else:
            TabWidget.textBrowser_3.append(f"生成特征失败(错误类型/代码：{code_dict.get(ret, self.libc.ZAZErr2Str(ret))})")
            # self.close_device()

    def get_image(self):
        TabWidget.textBrowser_3.clear()
        store_id, _ = QInputDialog.getText(self, "设定Flash存放地址", "请输入一个0-9999之间的数字:", QLineEdit.Normal,
                                           str(random.randint(0, 9999)))
        if store_id:
            self.thread = GetFingerprint(store_id, self.libc, self.handle)
            self.thread.step.connect(TabWidget.textBrowser_3.append)
            self.thread.start()

    def del_flash(self):
        store_id, _ = QInputDialog.getText(self, "删除指定模板", "请输入要删除的模板ID(0-9999的数字):", QLineEdit.Normal, "")
        if store_id:
            ret = self.libc.ZAZDelChar(self.handle, c_int(0xffffffff), int(store_id), 1)
            TabWidget.textBrowser_3.append(f"模板{store_id}删除成功" if ret == 0 else f"模板{store_id}删除失败")

    def clean_flash(self):
        ret = self.libc.ZAZEmpty(self.handle, c_int(0xffffffff))
        TabWidget.textBrowser_3.append("成功清空指纹库" if ret == 0 else "清空指纹库失败")

    def get_template_num(self):
        num = c_int(0)
        ret = self.libc.ZAZTemplateNum(self.handle, c_int(0xffffffff), byref(num))
        TabWidget.textBrowser_3.append(f"有效模板总数为{num.value}" if ret == 0 else "获取有效模板总数失败")


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
                    TabWidget.pushButton_openCam.setText("关闭摄像头")
                else:
                    self.camera.stop()
                    self.is_opened = False
                    TabWidget.pushButton_openCam.setText("开启摄像头")

    def capture(self):
        cap = QCameraImageCapture(self.camera)
        cap.setCaptureDestination(QCameraImageCapture.CaptureToFile)
        cap.capture("C:/Users/Nehcknarf/PycharmProjects/midtool/test")
        TabWidget.label_cap.setText("拍照成功，存储于工具目录下 test.jpg")


class Arcsoft(QWidget):
    def __init__(self):
        super().__init__()
        self.thread = QThread()

        TabWidget.pushButton_generator.clicked.connect(self.generator)
        TabWidget.pushButton_checkLicense.clicked.connect(self.check_active)
        # TabWidget.pushButton_upload.clicked.connect(self.upload)

    @staticmethod
    def check_active():
        hospital = TabWidget.lineEdit_4.text()

        if QFile.exists(f'/nubomed/{hospital}/conf/arcsoftActiveFile.dat') \
                or QFile.exists(f'/nubomed/{hospital}/conf/arcsoftActiveFile2.dat'):
            TabWidget.textBrowser_arcsoft.setText("✔ 已激活")
        else:
            TabWidget.textBrowser_arcsoft.setText("× 未激活")

    def generator(self):
        TabWidget.textBrowser_arcsoft.clear()
        TabWidget.textBrowser_arcsoft.setPlainText("执行脚本：/nubomed/arcsoft/arcsoftsetup.sh")
        password, _ = QInputDialog.getText(self, "提升权限", "请输入Root密码:", QLineEdit.Normal, "")

        self.thread = Commander(f"/bin/sh /nubomed/arcsoft/arcsoftsetup.sh {password}")
        self.thread.stdout.connect(TabWidget.textBrowser_arcsoft.append)
        self.thread.start()

    # def upload(self):
    #     request = QNetworkRequest()
    #     request.setUrl(QUrl("http://localhost:8080/api/login"))
    #     request.setRawHeader(b"Content-Type", b"application/json")
    #     request.setRawHeader(b"Content-Length", b"54")
    #     request.setRawHeader(b"Host", b"localhost:8080")
    #
    #     QJsonObject = QJsonDocument.fromJson(QByteArray()).object()  # 创建空的QJsonObject对象
    #     QJsonObject["username"] = "admin"
    #     QJsonObject["password"] = "admin"
    #     QJsonObject["recaptcha"] = ""
    #     data = QJsonDocument(QJsonObject).toJson(QJsonDocument.Compact)
    #
    #     manager = QNetworkAccessManager()
    #     reply = manager.post(request, data)
    #     # 同步
    #     loop = QEventLoop()
    #     reply.finished.connect(loop.quit)
    #     loop.exec_()
    #
    #     if reply.error() == QNetworkReply.NoError:
    #         print('Success')
    #     else:
    #         print('Error')
    #
    #     token = reply.readAll()
    #     print(token)
    #     # 异步
    #     # reply.finished.connect(self.parse)
    #
    #     file_name = "midtool.ui"
    #
    #     request.setUrl(QUrl(f"http://localhost:8080/api/resources/{file_name}?override=ture"))
    #
    #     multi_part = QHttpMultiPart(QHttpMultiPart.FormDataType)
    #
    #     text_part = QHttpPart()
    #     text_part.setRawHeader(b"Host", b"localhost:8080")
    #     text_part.setRawHeader(b"X-Auth", token)
    #     # text_part.setRawHeader(b"Content-Disposition", b'form-data; name=""')
    #     # text_part.setBody(b"")
    #
    #     file_part = QHttpPart()
    #     file_part.setRawHeader(b"Content-Type", b"text/plain")
    #     file_part.setRawHeader(b"Content-Disposition", b'form-data; name="file"')
    #     file = QFile(file_name)
    #     file.open(QIODevice.ReadOnly)
    #     file_part.setBodyDevice(file)
    #     file.setParent(multi_part)
    #
    #     multi_part.append(text_part)
    #     multi_part.append(file_part)
    #
    #     manager = QNetworkAccessManager()
    #     reply = manager.post(request, multi_part)
    #     multi_part.setParent(reply)
    #
    #     # 同步
    #     loop = QEventLoop()
    #     reply.finished.connect(loop.quit)
    #     loop.exec_()
    #
    #     if reply.error() == QNetworkReply.NoError:
    #         print('Success')
    #     else:
    #         print('Error')
    #
    #     response = reply.readAll()
    #     print(response)

    # def parse(self):
    #     responseData = self.reply.readAll()
    #     print(responseData)
    #     if self.reply.error() == QNetworkReply.NoError:
    #         print('Success')
    #     else:
    #         print('Error')


class Scan(QWidget):
    def __init__(self):
        super().__init__()
        self.thread = QThread()
        self.ser = QSerialPort()
        self.ser.readyRead.connect(self.read)
        self.thread = Serial(self.ser)
        self.thread.pinout.connect(TabWidget.textBrowser_4.append)

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
        self.thread.start()

    def close(self):
        if self.ser.isOpen():
            self.ser.close()
            TabWidget.textBrowser_4.append("设备已关闭")
            TabWidget.pushButton_openDevice_2.setEnabled(True)
            TabWidget.pushButton_closeDevice_2.setEnabled(False)

    @staticmethod
    def cls():
        TabWidget.textBrowser_4.clear()


if __name__ == "__main__":
    QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)

    app = QApplication(sys.argv)
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
        # 本地测试
        # TabWidget = loader.load("./midtool.ui")
        # 生产环境
        TabWidget = loader.load("/nubomed/midtool/midtool.ui")

        log = LogBrowser()
        ter = Terminal()
        yml = YamlConfig()
        file = FileManager()
        fp = FingerPrint()
        cam = Camera()
        arc = Arcsoft()
        scan = Scan()

        TabWidget.show()

        sys.exit(app.exec_())

import os
import sys
from collections import deque
from ctypes import *

import PySide2.QtQuick
from PySide2.QtMultimedia import QCamera, QCameraImageCapture, QCameraViewfinderSettings
from PySide2.QtMultimediaWidgets import QCameraViewfinder
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication, QWidget, QFileDialog, QInputDialog, QMessageBox, QLineEdit, QFileSystemModel
from PySide2.QtCore import Qt, QThread, Signal, QDir, QFile, QIODevice, QTextStream, QRegExp, QProcess, QSize, \
    QModelIndex
from PySide2.QtGui import QTextCursor, QTextCharFormat, QColor
from PySide2.QtSerialPort import QSerialPortInfo


# Ubuntu 22.04
# os.environ["QT_QPA_PLATFORM"] = "wayland"
# Ubuntu 20.04
os.environ["QT_QPA_PLATFORM"] = "xcb"
# DEBUG
# os.environ["QT_DEBUG_PLUGINS"] = "1"
# 虚拟键盘
os.environ["QT_IM_MODULE"] = "qtvirtualkeyboard"

# 指昂指纹模块返回码字典
code_dict = {0: "执行成功", 1: "数据包接收错误", 2: "传感器上没有手指", 3: "录入指纹图象失败", 4: "指纹太淡", 5: "指纹太糊",
             6: "指纹太乱", 7: "指纹特征点太少", 8: "指纹不匹配", 9: "没搜索到指纹", 10: "特征合并失败", 11: "地址号超出指纹库范围",
             12: "从指纹库读模板出错", 13: "上传特征失败", 14: "模块不能接收后续数据包", 15: "上传图象失败", 16: "删除模板失败",
             17: "清空指纹库失败", 18: "不能进入休眠", 19: "口令不正确", 20: "系统复位失败", 21: "无效指纹图象"}


class Commander(QThread):
    stdout = Signal(str)

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

        while process_command.state() != QProcess.NotRunning:
            QApplication.processEvents()
            if QThread.currentThread().isInterruptionRequested():
                break
            if process_command.waitForReadyRead():
                stdout = bytes(process_command.readAllStandardOutput()).decode("utf8").rstrip('\n')
                self.stdout.emit(stdout)

        self.stdout.emit("执行完毕！")


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


class GetFingerprint(QThread):
    step = Signal(str)

    def __init__(self, store_id, dll, handle):
        super().__init__()
        self.store_id = store_id
        self.dll = dll
        self.handle = handle

    def emit_state(self, code, func_str):
        if code == 0:
            self.step.emit(f"{func_str}成功")
        else:
            self.step.emit(f"{func_str}失败(错误类型/代码：{code_dict.get(code, self.dll.ZAZErr2Str(code))})")
            return

    def run(self):
        nAddr = c_int(0xffffffff)
        self.step.emit("请将手指平放在传感器上...")
        ret = 2  # 传感器上没有手指
        timeout = 0
        while ret == 2 and timeout <= 100:
            QApplication.processEvents()
            ret = self.dll.ZAZGetImage(self.handle, nAddr)
            timeout += 1
        if timeout == 101:
            self.step.emit("超时！请重新采集")
            return
        self.emit_state(ret, "第一次采集指纹")

        ret = self.dll.ZAZGenChar(self.handle, nAddr, 2)
        self.emit_state(ret, "生成特征A")

        self.step.emit("请抬起手指！")
        QThread.sleep(1)
        self.step.emit("请再次将手指平放在传感器上...")

        ret = 2  # 传感器上没有手指
        timeout = 0
        while ret == 2 and timeout <= 100:
            QApplication.processEvents()
            ret = self.dll.ZAZGetImage(self.handle, nAddr)
            timeout += 1
        if timeout == 101:
            self.step.emit("超时！请重新采集")
            return
        self.emit_state(ret, "第二次采集指纹")

        ret = self.dll.ZAZGenChar(self.handle, nAddr, 1)
        self.emit_state(ret, "生成特征B")

        ret = self.dll.ZAZRegModule(self.handle, nAddr)
        self.emit_state(ret, "合并特征")

        ret = self.dll.ZAZStoreChar(self.handle, nAddr, 1, int(self.store_id))
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
        # UI
        TabWidget.listButton.clicked.connect(self.pm2_list)
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

    def common_command(self, command):
        command, password = self.promote(command)

        TabWidget.textBrowser_2.clear()
        TabWidget.textBrowser_2.setPlainText(f"执行命令：{command}")
        self.thread = Commander(command, password)
        self.thread.stdout.connect(TabWidget.textBrowser_2.append)
        self.thread.start()

    def pm2_list(self):
        self.common_command("pm2 list -m")

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


class Serial(QWidget):
    def __init__(self):
        super().__init__()
        self.serial_port_info = QSerialPortInfo
        # 本地测试
        # self.so = cdll.LoadLibrary("./libapit.so")
        # 生产环境
        self.so = cdll.LoadLibrary("/nubomed/midtool/libapit.so")
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

    def get_port(self):
        TabWidget.comboBox_portName.addItems([com.portName() for com in self.serial_port_info.availablePorts()])

    def get_baud_rate(self):
        return map(str, self.serial_port_info.standardBaudRates())

    def open_device(self):
        TabWidget.textBrowser_3.clear()
        port_name = TabWidget.comboBox_portName.currentText()
        baudrate = TabWidget.comboBox_BaudRate.currentText()

        if QSerialPortInfo(port_name).isBusy():
            return

        nDeviceType = 1  # 串口设备
        iCom = int(port_name[-1])  # 串口号 1-16
        iBaud = int(int(baudrate) / 9600)  # （9600*N）bps,其中N=1—12(默认出厂N=6，即57600bps)

        ret = self.so.ZAZOpenDeviceEx(byref(self.handle), nDeviceType, iCom, iBaud)
        print(ret)  # 0 表示成功
        if ret == 0:
            TabWidget.pushButton_openDevice.setEnabled(False)
            TabWidget.pushButton_closeDevice.setEnabled(True)
            TabWidget.pushButton_getFingerprintNum.setEnabled(True)
            TabWidget.pushButton_getfingerprint.setEnabled(True)
            TabWidget.pushButton_searchfp.setEnabled(True)
            TabWidget.pushButton_del.setEnabled(True)
            TabWidget.pushButton_empty.setEnabled(True)
        else:
            QMessageBox.critical(self, "Error", "设备未正确打开！")

    def close_device(self):
        ret = self.so.ZAZCloseDeviceEx(self.handle)
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
        while ret == 2 and timeout <= 100:
            QApplication.processEvents()
            ret = self.so.ZAZGetImage(self.handle, nAddr)
            timeout += 1
        if timeout == 101:
            TabWidget.textBrowser_3.append("超时！请重新采集")
            # self.close_device()
            return
        if ret == 0:
            TabWidget.textBrowser_3.append("成功获取指纹")
        else:
            # self.close_device()
            return

        ret = self.so.ZAZGenChar(self.handle, nAddr, 1)
        if ret == 0:
            TabWidget.textBrowser_3.append("生成特征成功")
            code = self.so.ZAZSearch(self.handle, c_int(0xffffffff), 1, 0, 9999, byref(i), byref(score))
            TabWidget.textBrowser_3.append("***如果返回类型/代码为”没搜索到指纹“，且匹配得分为0，则匹配得到的ID不正确，忽略即可***")
            TabWidget.textBrowser_3.append(f"返回类型/代码：{code_dict.get(code, self.so.ZAZErr2Str(code))}")
            TabWidget.textBrowser_3.append("匹配的ID：未找到" if i.value == 65022 else f"匹配的ID：{str(i.value)}")
            TabWidget.textBrowser_3.append(f"匹配得分：{str(score.value)}")
        else:
            TabWidget.textBrowser_3.append(f"生成特征失败(错误类型/代码：{code_dict.get(ret, self.so.ZAZErr2Str(ret))})")
            # self.close_device()

    def get_image(self):
        TabWidget.textBrowser_3.clear()
        store_id, _ = QInputDialog.getText(self, "设定Flash存放地址", "请输入一个0-9999之间的数字:", QLineEdit.Normal, "")
        if store_id:
            self.thread = GetFingerprint(store_id, self.so, self.handle)
            self.thread.step.connect(TabWidget.textBrowser_3.append)
            self.thread.start()

    def del_flash(self):
        store_id, _ = QInputDialog.getText(self, "删除指定模板", "请输入要删除的模板ID(0-9999的数字):", QLineEdit.Normal, "")
        if store_id:
            ret = self.so.ZAZDelChar(self.handle, c_int(0xffffffff), int(store_id), 1)
            TabWidget.textBrowser_3.append(f"模板{store_id}删除成功" if ret == 0 else f"模板{store_id}删除失败")

    def clean_flash(self):
        ret = self.so.ZAZEmpty(self.handle, c_int(0xffffffff))
        TabWidget.textBrowser_3.append("成功清空指纹库" if ret == 0 else "清空指纹库失败")

    def get_template_num(self):
        num = c_int(0)
        ret = self.so.ZAZTemplateNum(self.handle, c_int(0xffffffff), byref(num))
        TabWidget.textBrowser_3.append(f"有效模板总数为{num.value}" if ret == 0 else "获取有效模板总数失败")


class Camera(QWidget):
    def __init__(self):
        super().__init__()
        self.camera = QCamera()
        self.camera.setCaptureMode(QCamera.CaptureViewfinder)
        self.is_opened = False

        view_finder_settings = QCameraViewfinderSettings()
        view_finder_settings.setResolution(640, 480)
        view_finder_settings.setMaximumFrameRate(30)
        self.camera.setViewfinderSettings(view_finder_settings)

        # self.camera_info = QCameraInfo()
        # self.camera_list = self.camera_info.availableCameras()

        self.view_finder = QCameraViewfinder()
        self.camera.setViewfinder(self.view_finder)

        # TabWidget.comboBox_cam.addItems([cam.description() for cam in self.camera_list])
        TabWidget.pushButton_openCam.clicked.connect(self.cam_switch)
        TabWidget.pushButton_capture.clicked.connect(self.capture)
        # TODO 更好的方案？
        TabWidget.horizontalLayout_16.addWidget(self.view_finder)

        self.cap = QCameraImageCapture(self.camera)
        self.cap.setCaptureDestination(QCameraImageCapture.CaptureToFile)

    def cam_switch(self):
        if not self.is_opened:
            self.camera.start()
            self.is_opened = True
            TabWidget.pushButton_openCam.setText("关闭摄像头")
        else:
            self.camera.stop()
            self.is_opened = False
            TabWidget.pushButton_openCam.setText("开启摄像头")

    def capture(self):
        self.cap.capture("C:/Users/Nehcknarf/PycharmProjects/midtool/test")
        TabWidget.label_cap.setText("拍照成功，存储于工具目录下 test.jpg")


class Arcsoft(QWidget):
    def __init__(self):
        super().__init__()
        self.thread = QThread()

        TabWidget.pushButton_generator.clicked.connect(self.generator)
        TabWidget.pushButton_checkLicense.clicked.connect(self.check_active)

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


if __name__ == "__main__":
    # QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)

    app = QApplication(sys.argv)
    # app.setStyle('Fusion')

    loader = QUiLoader()
    # 本地测试
    # TabWidget = loader.load("./midtool.ui")
    # 生产环境
    TabWidget = loader.load("/nubomed/midtool/midtool.ui")

    l = LogBrowser()
    t = Terminal()
    y = YamlConfig()
    f = FileManager()
    s = Serial()
    c = Camera()
    a = Arcsoft()

    TabWidget.show()

    sys.exit(app.exec_())

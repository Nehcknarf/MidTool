import sys
from collections import deque

from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication, QWidget, QFileDialog, QInputDialog, QMessageBox, QLineEdit
from PySide2.QtCore import Qt, QCoreApplication, QThread, Signal, QDir, QFile, QIODevice, QTextStream, QRegExp, QProcess
from PySide2.QtGui import QTextCursor, QTextCharFormat, QColor


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

    def start_mid(self):
        self.common_command("pm2 start 0 -m")

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
        self.file_name = ""
        self.dir = ""
        self.process = QProcess()
        self.msg_box = QMessageBox()

    def duplicate_popup(self):
        self.msg_box = QMessageBox()
        self.msg_box.setWindowTitle("错误")
        self.msg_box.setText("文件已经存在")
        self.msg_box.setStandardButtons(QMessageBox.Ok)
        self.msg_box.setIcon(QMessageBox.Information)
        self.msg_box.exec()

    # def add_file(self):
    #     if form.lineEdit_2.text() in [form.listWidget.item(i).text() for i in range(form.listWidget.count())]:
    #         self.duplicate_popup()
    #     else:
    #         form.listWidget.addItem(form.lineEdit_2.text())
    #
    # def del_file(self):
    #     TabWidget.listWidget.takeItem(TabWidget.listWidget.currentRow())
    #
    # def open_file(self):
    #     self.file_name, _ = QFileDialog.getOpenFileName(self, "打开文件...", "/home", "All files (*.*);;")
    #     # self.dir = QFileDialog.getExistingDirectory(self, "Open Directory", "/home",
    #     #                                             QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)
    #     if self.file_name in [TabWidget.listWidget.item(i).text() for i in range(TabWidget.listWidget.count())]:
    #         self.duplicate_popup()
    #     else:
    #         if self.file_name:
    #             TabWidget.listWidget.addItem(self.file_name)
    #
    # def get_usb_device_info(self):
    #     if self.watcher.fileChanged:
    #         # self.process.startCommand("blkid -d -c /dev/null")
    #         self.process.start("blkid -d -c /dev/null")
    #         self.process.waitForFinished()
    #         stdout = bytes(self.process.readAllStandardOutput()).decode("utf8")
    #         ret = re.findall(r"(/dev/sd[a-z])", stdout)
    #         form.comboBox.addItems(ret)
    #
    # def mount_usb_device(self):
    #     # self.process.startCommand("mkdir -p /mnt/usb")
    #     self.process.start("mkdir -p /mnt/usb")
    #     self.process.waitForFinished()
    #     device = form.comboBox.currentText()
    #     print(device)
    #     # self.process.startCommand(f"mount {device} /mnt/usb")
    #     self.process.start(f"mount {device} /mnt/usb")
    #     self.process.waitForFinished()
    #     if self.process.finished:
    #         self.msg_box.setText("USB设备成功挂载！")
    #         self.msg_box.exec()

    def copy_to_usb(self):
        pass


if __name__ == "__main__":
    QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)

    app = QApplication(sys.argv)
    # app.setStyle('Fusion')

    loader = QUiLoader()
    # 本地测试
    # TabWidget = loader.load("/mnt/c/Users/Nehcknarf/PycharmProjects/midtool/midtool.ui")
    # 生产环境
    TabWidget = loader.load("/nubomed/midtool/midtool.ui")

    f = LogBrowser()
    t = Terminal()
    y = YamlConfig()

    TabWidget.show()

    sys.exit(app.exec_())

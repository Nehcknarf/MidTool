import sys
from collections import deque

from PySide2.QtCore import QFile, QIODevice, QTextStream, QRegExp, Qt, QThread, QProcess, Signal, QFileSystemWatcher, \
    QCoreApplication
from PySide2.QtGui import QTextCursor, QTextCharFormat, QColor
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication, QFileDialog, QWidget, QInputDialog, QLineEdit


# 本地测试
log_path = "/mnt/c/Users/Nehcknarf/PycharmProjects/midtool"
# 生产环境
# log_path = "/nubomed"


class Worker(QThread):
    stdout = Signal(str)

    def __init__(self, command, password):
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


class LogBrowser(QWidget):
    def __init__(self):
        super().__init__()
        self.q = deque()
        self.keyword_len = 0
        self.thread = QThread()
        # UI
        TabWidget.textBrowser.ensureCursorVisible()
        TabWidget.openfileButton.clicked.connect(self.open_log)
        TabWidget.tailButton.clicked.connect(self.tail_log)
        TabWidget.searchButton.clicked.connect(self.search)
        TabWidget.prevButton.clicked.connect(self.prev)
        TabWidget.nextButton.clicked.connect(self.next)
        # TabWidget.lineEdit.textChanged.connect(self.search)
        TabWidget.match_case.stateChanged.connect(self.search)
        TabWidget.match_word.stateChanged.connect(self.search)

    def open_log(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择日志文件", log_path, "日志文件 (*.log)")
        if path:
            file = QFile(path)
            if file.open(QIODevice.ReadOnly | QIODevice.Text):
                content = QTextStream(file).readAll()
                TabWidget.textBrowser.setPlainText(content)
            file.close()

    def tail_log(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择待监控的日志文件", log_path, "日志文件 (*.log)")
        if path:
            TabWidget.textBrowser.clear()
            self.thread = Worker(f"tail -f -n 30 {path}", None)
            self.thread.stdout.connect(TabWidget.textBrowser.setPlainText)
            self.thread.start()

    def highlight(self, pos):
        cursor = TabWidget.textBrowser.textCursor()
        cursor.setPosition(pos)
        cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, self.keyword_len)
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
        if TabWidget.match_word.isChecked():
            keyword = f"\\b{keyword}\\b"
        if not keyword:
            return

        # 恢复默认的颜色
        cursor = TabWidget.textBrowser.textCursor()
        cursor.select(QTextCursor.Document)
        cursor.setCharFormat(QTextCharFormat())
        cursor.clearSelection()
        TabWidget.textBrowser.setTextCursor(cursor)

        fmt = QTextCharFormat()
        fmt.setBackground(QColor.fromRgbF(1.000000, 1.000000, 0.000000, 1.000000))

        if TabWidget.match_case.isChecked():
            match_case = Qt.CaseSensitive
        else:
            match_case = Qt.CaseInsensitive
        rx = QRegExp(keyword, match_case)
        TabWidget.textBrowser.moveCursor(QTextCursor.Start)
        cursor = TabWidget.textBrowser.textCursor()

        # 循环查找设置颜色
        self.q.clear()
        log = TabWidget.textBrowser.toPlainText()
        pos = rx.indexIn(log, 0)
        if pos != -1:
            self.q.append(pos)
        while pos != -1:
            cursor.setPosition(pos)
            cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, self.keyword_len)
            cursor.mergeCharFormat(fmt)
            pos += rx.matchedLength()
            pos = rx.indexIn(log, pos)
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
        path, _ = QFileDialog.getOpenFileName(self, "选择Shell脚本", log_path, "Shell脚本 (*.sh)")
        if path:
            TabWidget.textBrowser_2.clear()
            self.thread = Worker(f"/bin/sh {path}", None)
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
        self.thread = Worker(command, password)
        self.thread.stdout.connect(TabWidget.textBrowser_2.append)
        self.thread.start()

    def common_command(self, command):
        command, password = self.promote(command)

        TabWidget.textBrowser_2.clear()
        TabWidget.textBrowser_2.setPlainText(f"执行命令：{command}")
        self.thread = Worker(command, password)
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
        self.common_command(f"wscat -c ws://localhost:{port}/websocket")

    def kill(self):
        if self.thread.isRunning():
            self.thread.requestInterruption()
            self.thread.quit()
            self.thread.wait()
        self.thread.deleteLater()


if __name__ == "__main__":
    QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)

    app = QApplication(sys.argv)
    # app.setStyle('Fusion')

    loader = QUiLoader()
    # 本地测试
    TabWidget = loader.load("/mnt/c/Users/Nehcknarf/PycharmProjects/midtool/midtool.ui")
    # 生产环境
    # TabWidget = loader.load("/nubomed/midtool/midtool.ui")

    f = LogBrowser()
    t = Terminal()

    TabWidget.show()

    sys.exit(app.exec_())

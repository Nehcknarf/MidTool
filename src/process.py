import os
import platform

from PySide6.QtCore import QObject, QProcess, Signal, Slot, QUrl
from PySide6.QtQml import QmlElement


QML_IMPORT_NAME = "src.process"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0

system = platform.system()

if system == "Linux":
    user = os.environ.get("USER")
    work_path = f"/home/{user}"
    shell = "/bin/bash -c \"{}\""
    coding = "UTF-8"
    sep = "\n"
elif system == "Windows":
    user = os.environ.get("UserName")
    work_path = f"C:/Users/{user}"
    shell = "powershell {}"
    coding = "GBK"
    sep = "\r\n"


@QmlElement
class Process(QObject):
    Stdout = Signal(str, arguments='output')

    def __init__(self):
        super().__init__()
        self.process_command = QProcess()
        self.process_command.readyReadStandardOutput.connect(self.handle_stdout)
        self.process_command.readyReadStandardError.connect(self.handle_stderr)
        self.process_command.stateChanged.connect(self.handle_state)
        self.process_command.finished.connect(self.finished)

    @Slot(str)
    def start(self, command, workdir=work_path, password=None):
        self.process_command.setWorkingDirectory(workdir)
        # self.process_command.setProcessChannelMode(QProcess.MergedChannels)
        if "sudo " in command:
            # Pipe
            process_echo = QProcess()
            process_echo.setStandardOutputProcess(self.process_command)
            process_echo.startCommand(f"echo {password}")
        self.process_command.startCommand(shell.format(command))

    @Slot()
    def kill(self):
        self.process_command.kill()

    def handle_stdout(self):
        data = self.process_command.readAllStandardOutput()
        stdout = bytes(data).decode(coding).rstrip(sep)
        self.Stdout.emit(stdout)

    def handle_stderr(self):
        data = self.process_command.readAllStandardError()
        stderr = bytes(data).decode(coding).rstrip(sep)
        self.Stdout.emit(stderr)

    def handle_state(self, state):
        states_dict = {
            QProcess.Starting: self.tr("Starting"),
            QProcess.Running: self.tr("Running"),
            QProcess.NotRunning: self.tr("Not running")
        }
        state_name = states_dict.get(state)
        self.Stdout.emit(self.tr("Process state changed: {}").format(state_name))

    def finished(self, exit_code, exit_status):
        self.Stdout.emit(self.tr("Process finished with exit code {}").format(exit_code))

    @Slot(QUrl)
    def start_middleware(self, qurl):
        path = qurl.toLocalFile()
        self.start(f"(supervisorctl start all; supervisorctl update all) || (pm2 start {path} -m; pm2 save -m)")

    @Slot()
    def restart_middleware(self):
        self.start(f"supervisorctl restart all || pm2 restart 0 -m")

    @Slot()
    def stop_middleware(self):
        self.start(f"supervisorctl stop all || pm2 stop 0 -m")

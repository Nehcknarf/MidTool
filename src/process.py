import platform

from PySide6.QtCore import QObject, QRunnable, Signal, Slot, QProcess, QCoreApplication


system = platform.system()


class WorkerSignals(QObject):
    stdout = Signal(str)
    verbose = Signal(str)


class Commander(QRunnable):
    def __init__(self, command, password=None, wd="/"):
        super().__init__()
        self.signals = WorkerSignals()
        self.process_command = None
        self.need_kill = False
        self.command = command
        self.password = password
        self.wd = wd

    @Slot()
    def run(self):
        self.process_command = QProcess()
        # self.process_command.setProcessChannelMode(QProcess.MergedChannels)
        # if self.command.__contains__("sudo"):
        #     # Pipe
        #     process_echo = QProcess()
        #     process_echo.setStandardOutputProcess(self.process_command)
        #     process_echo.startCommand(f"echo {self.password}")
        #     process_echo.waitForFinished()
        #
        # if system == "Linux":
        #     self.process_command.setWorkingDirectory(self.wd)

        self.process_command.readyReadStandardOutput.connect(self.handle_stdout)
        self.process_command.readyReadStandardError.connect(self.handle_stderr)
        self.process_command.stateChanged.connect(self.handle_state)
        self.process_command.finished.connect(self.cleanup)

        self.process_command.startCommand(f"/bin/sh -c \"{self.command}\"")
        # self.process_command.waitForStarted()
        
        # string = ""
        # while self.process_command.state() != QProcess.NotRunning:
        #     if self.need_kill:
        #         break
        #     if self.process_command.waitForReadyRead():
        #         if system == "Windows":
        #             stdout = bytes(self.process_command.readAllStandardOutput()).decode("gbk").rstrip('\r\n')
        #         elif system == "Linux":
        #             stdout = bytes(self.process_command.readAllStandardOutput()).decode("utf8").rstrip('\n')
        #         print(stdout)
        #         self.signals.stdout.emit(stdout)
        #         string += f"{stdout}\n"
        #
        # self.signals.verbose.emit(string)
        # self.signals.stdout.emit(QCoreApplication.translate("Commander", "Command has executed"))

    def kill(self):
        self.need_kill = True

    def handle_stderr(self):
        data = self.process_command.readAllStandardError()
        stderr = bytes(data).decode("utf8").rstrip('\n')
        print(stderr)
        self.signals.stdout.emit(stderr)

    def handle_stdout(self):
        data = self.process_command.readAllStandardOutput()
        stdout = bytes(data).decode("utf8").rstrip('\n')
        print(stdout)
        self.signals.stdout.emit(stdout)

    def handle_state(self, state):
        states = {
            QProcess.NotRunning: 'Not running',
            QProcess.Starting: 'Starting',
            QProcess.Running: 'Running',
        }
        state_name = states[state]
        print(f"State changed: {state_name}")
        self.signals.stdout.emit(f"State changed: {state_name}")

    def cleanup(self):
        print("Process finished.")
        self.signals.stdout.emit("Process finished.")
        self.process_command = None


from PySide6.QtCore import QObject, QProcess, Signal, Slot

from utils.adapter import work_path, shell, coding, sep


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
        if "sudo" in command:
            # Pipe
            command = command.replace("sudo", "sudo -S")
            process_echo = QProcess()
            process_echo.setStandardOutputProcess(self.process_command)
            process_echo.startCommand(f"echo {password}")
            process_echo.waitForFinished()
        self.process_command.startCommand(shell.format(command))

    @Slot(str)
    def write(self, data):
        data += sep
        ret = self.process_command.write(data.encode(coding))
        if ret == -1:
            self.Stdout.emit(self.tr("Error occurred. Please start script first."))

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
        self.Stdout.emit(self.tr("*** Process state changed: {} ***").format(state_name))

    def finished(self, exit_code, exit_status):
        self.Stdout.emit(self.tr("*** Process finished with exit code {} ***").format(exit_code))

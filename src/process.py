import glob

from PySide6.QtCore import QObject, QProcess, Signal, Slot, QUrl
from PySide6.QtQml import QmlElement

from utils.env import root_path, work_path, shell, coding, sep

QML_IMPORT_NAME = "src.process"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0


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
        if "sudo" in command:
            # Pipe
            command = command.replace("sudo", "sudo -S")
            process_echo = QProcess()
            process_echo.setStandardOutputProcess(self.process_command)
            process_echo.startCommand(f"echo {password}")
            process_echo.waitForFinished()
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
        self.Stdout.emit(self.tr("*** Process state changed: {} ***").format(state_name))

    def finished(self, exit_code, exit_status):
        self.Stdout.emit(self.tr("Process finished with exit code {}").format(exit_code))

    @Slot(str)
    def start_middleware_sv(self, password):
        self.start(f"sudo supervisorctl start all", password=password)

    @Slot(QUrl)
    def start_middleware_pm2(self, qurl):
        path = qurl.toLocalFile()
        self.start(f"pm2 start {path} -m && pm2 save -m")

    @Slot(str)
    def restart_middleware(self, password):
        self.start(f"sudo supervisorctl restart all || pm2 restart 0 -m", password=password)

    @Slot(str)
    def stop_middleware(self, password):
        self.start(f"sudo supervisorctl stop all || pm2 stop 0 -m", password=password)

    @Slot(int)
    def install_middleware(self, type):
        if wd := glob.glob("/nubomed/consumable-cabinet-service_V*/"):
            self.start(f"bash install.sh {type}", wd[0])
        else:
            self.Stdout.emit(self.tr("Please confirm middleware install package has already unzip under "
                                     "\"/nubomed/consumable-cabinet-service_V*/\""))

    @Slot(QUrl)
    def update_middleware(self, qurl):
        update_pkg_path = qurl.toLocalFile()
        self.start(f"bash upgrade_version.sh {update_pkg_path}", f"{root_path}/script/")

    @Slot(str, str, str, str)
    def activate_arcsoft(self, key_part_1, key_part_2, key_part_3, key_part_4):
        app_id = "F3sE2YzxMYy4VAFCRiLCz9NzBmQeCMB8nN2fVyo7F4Ca"
        sdk_key = "8bLYHqy1QaCzqbQ5PrDuQFGfmk1QJneYV216uSjDBq7v"
        key_string = "-".join([key_part_1, key_part_2, key_part_3, key_part_4]).upper()
        self.start(f"bash arsoft_Active.sh {app_id} {sdk_key} {key_string}", f"{root_path}/script/")

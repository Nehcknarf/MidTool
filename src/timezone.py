from PySide6.QtCore import Signal, Slot, Property
from PySide6.QtQml import QmlElement

from process import Process
from src.utils.env import coding, sep


QML_IMPORT_NAME = "src.time"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0


@QmlElement
class TimeEditor(Process):
    timezoneChanged = Signal()

    def __init__(self):
        super().__init__()
        self.stdout = ""

    def handle_stdout(self):
        data = self.process_command.readAllStandardOutput()
        self.stdout += bytes(data).decode(coding).rstrip(sep)

    def get_timezones(self):
        self.start("timedatectl list-timezones")
        self.process_command.waitForFinished()
        return self.stdout.split()

    timezones = Property(list, get_timezones, notify=timezoneChanged)

    @Slot(str, str)
    def set_timezone(self, timezone, password):
        self.start(f"sudo timedatectl set-timezone {timezone}", password=password)

    @Slot(str, str)
    def set_time(self, time, password):
        self.start(f"sudo timedatectl set-time '{time}'", password=password)

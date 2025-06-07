import zoneinfo

from PySide6.QtCore import Signal, Slot, Property
from PySide6.QtQml import QmlElement

from process import Process
from utils.adapter import root_path
from utils.log import logger


QML_IMPORT_NAME = "src.time"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0


@QmlElement
class TimeEditor(Process):
    timezoneChanged = Signal()

    def __init__(self):
        super().__init__()

    def get_timezones(self):
        timezones = list(zoneinfo.available_timezones())
        timezones.sort()
        return timezones

    timezones = Property(list, get_timezones, notify=timezoneChanged)

    @Slot(str, str)
    def set_timezone(self, timezone, password):
        logger.info(f"Set system timezone to {timezone}")
        self.start(f"sudo timedatectl set-timezone {timezone}", password=password)

    @Slot(str, str)
    def set_time(self, time, password):
        logger.info(f"Set system time to {time}")
        self.start(f"sudo timedatectl set-time '{time}'", password=password)

    @Slot(str, str)
    def add_ntp_servers(self, ntp_servers, password):
        logger.info(f"Add {ntp_servers} as NTP servers")
        self.start(f"sudo bash ntp.sh {ntp_servers}", workdir=f"{root_path}/script/", password=password)

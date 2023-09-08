import zoneinfo

from PySide6.QtCore import Signal, Slot, Property
from PySide6.QtQml import QmlElement

from process import Process


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
        self.start(f"sudo timedatectl set-timezone {timezone}", password=password)

    @Slot(str, str)
    def set_time(self, time, password):
        self.start(f"sudo timedatectl set-time '{time}'", password=password)

    @Slot(str, str)
    def add_ntp_servers(self, ntp_servers, password):
        self.start(f"sudo sed -i 's/^#*NTP=.*/NTP={ntp_servers}/' /etc/systemd/timesyncd.conf && systemctl restart systemd-timesyncd", password=password)

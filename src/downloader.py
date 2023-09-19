import os
import glob
from zipfile import ZipFile
from datetime import date, datetime, timedelta

from PySide6.QtCore import Slot, QUrl, QObject, Signal
from PySide6.QtQml import QmlElement

from utils.adapter import middleware_log_path, work_path


QML_IMPORT_NAME = "src.logDownloader"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0


@QmlElement
class LogDownloader(QObject):
    Output = Signal()

    realtime_system_log_path = [
        "/var/log/syslog",
        "/var/log/dmesg",
        "/var/log/kern.log",
        f"{work_path}/.local/share/xorg/Xorg.0.log"]

    archived_system_log_path_pattern = [
        "/var/log/syslog.*",
        "/var/log/dmesg.*",
        "/var/log/kern.log.*",
        f"{work_path}/.local/share/xorg/Xorg.0.log.*"]

    def get_date_list(self, start_date, end_date):
        delta_days = (end_date - start_date).days
        if delta_days >= 0:
            date_list = []
            for _ in range(delta_days + 1):
                date_list.append(start_date.strftime("%Y-%m-%d"))
                start_date += timedelta(days=1)
            return date_list
        else:
            self.Output.emit(self.tr("Start Date must be earlier than or equal to End Date"))
            return

    def archived_log_filter(self, path_pattern, start_date, end_date, myzip):
        for path in glob.glob(path_pattern):
            archived_log_date = date.fromtimestamp(os.path.getmtime(path)) - timedelta(days=1)
            if start_date <= archived_log_date <= end_date:
                try:
                    myzip.write(path)
                except Exception as err:
                    self.Output.emit(str(err))
                else:
                    self.Output.emit(self.tr("Add archived {} to the zip").format(path))
            # else:
            #     self.Stdout.emit(self.tr("{} isn't between date range, skip").format(path))

    @Slot(QUrl, str, str, int)
    def download(self, qurl, start_date, end_date, log_type):
        save_dir = qurl.toLocalFile()
        start_date = date.fromisoformat(start_date)
        end_date = date.fromisoformat(end_date)

        date_list = self.get_date_list(start_date, end_date)
        today = datetime.now()

        # 中台日志
        if log_type == 1:
            with ZipFile(f"{save_dir}/mid-log-{today.strftime('%Y%m%d%H%M%S')}.zip", 'a') as myzip:
                # 实时日志
                if today.strftime("%Y-%m-%d") in date_list:
                    mid_log_path = f"{middleware_log_path}/mid.log"
                    try:
                        myzip.write(mid_log_path)
                    except Exception as err:
                        self.Output.emit(str(err))
                    else:
                        date_list.remove(today.strftime("%Y-%m-%d"))
                        self.Output.emit(self.tr("Add real-time {} to the zip").format(mid_log_path))
                # 归档历史日志
                for date_str in date_list:
                    mid_log_path = f"{middleware_log_path}/mid-{date_str}-1.log.gz"
                    try:
                        myzip.write(mid_log_path)
                    except Exception as err:
                        self.Output.emit(str(err))
                    else:
                        self.Output.emit(self.tr("Add archived {} to the zip").format(mid_log_path))

            self.Output.emit(self.tr("Middleware logs saved in {}").format(save_dir))
        # Ubuntu 系统日志
        elif log_type == 2:
            with ZipFile(f"{save_dir}/sys-log-{today.strftime('%Y%m%d%H%M%S')}.zip",'a') as myzip:
                if end_date.strftime("%Y-%m-%d") == today.strftime("%Y-%m-%d"):
                    for path in self.realtime_system_log_path:
                        try:
                            myzip.write(path)
                        except Exception as err:
                            self.Output.emit(str(err))
                        else:
                            self.Output.emit(self.tr("Add real-time {} to the zip").format(path))

                for path_pattern in self.archived_system_log_path_pattern:
                    self.archived_log_filter(path_pattern, start_date, end_date, myzip)

            self.Output.emit(self.tr("System logs saved in {}").format(save_dir))

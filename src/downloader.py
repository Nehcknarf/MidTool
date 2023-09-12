from PySide6.QtCore import Slot, QUrl
from PySide6.QtQml import QmlElement

from process import Process
from utils.env import root_path


QML_IMPORT_NAME = "src.logDownloader"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0


@QmlElement
class LogDownloader(Process):
    @Slot(QUrl, str, str, str)
    def download(self, qurl, start_date, end_date, log_type):
        save_dir = qurl.toLocalFile()
        self.start(f"bash logDownload.sh {save_dir} {start_date} {end_date} {log_type}", f"{root_path}/script/")

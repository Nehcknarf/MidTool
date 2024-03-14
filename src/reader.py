from PySide6.QtCore import Slot, QUrl
from PySide6.QtQml import QmlElement

from process import Process
from utils.log import logger
from utils.adapter import root_path


QML_IMPORT_NAME = "src.reader"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0


@QmlElement
class Reader(Process):
    @Slot()
    def start_config(self):
        logger.info(f"Try to config RFID reader...")
        self.start(f"bash start.sh", f"{root_path}/script/RFIDReader/")

    @Slot(QUrl, str)
    def record(self, qurl, text):
        save_dir = qurl.toLocalFile()
        with open(f"{save_dir}/reader_records.txt", "w") as f:
            f.write(text)

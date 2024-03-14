from PySide6.QtCore import Slot
from PySide6.QtQml import QmlElement

from process import Process
from utils.log import logger
from utils.adapter import root_path


QML_IMPORT_NAME = "src.activation"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0


@QmlElement
class Activation(Process):
    @Slot(str, str, str, str)
    def activate_arcsoft(self, key_part_1, key_part_2, key_part_3, key_part_4):
        app_id = "F3sE2YzxMYy4VAFCRiLCz9NzBmQeCMB8nN2fVyo7F4Ca"
        sdk_key = "8bLYHqy1QaCzqbQ5PrDuQFGfmk1QJneYV216uSjDBq7v"
        key_string = "-".join([key_part_1, key_part_2, key_part_3, key_part_4]).upper()
        logger.info(f"Try to activate ArcSoft using KEY: {key_string}")
        self.start(f"bash arsoftActive.sh {app_id} {sdk_key} {key_string}", f"{root_path}/script/Activate")

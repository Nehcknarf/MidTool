import json

from ruamel.yaml import YAML

from PySide6.QtCore import QObject, Signal, Slot, Property
from PySide6.QtQml import QmlElement

from utils.log import logger
from utils.adapter import product_type, nvr_cfg_path, extern_cfg_path, action_delay_cfg_path, sync_cfg_path, \
    mcc_cfg_path, ws_cfg_path, finger_cfg_path, lang_cfg_path

QML_IMPORT_NAME = "src.editor"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0


@QmlElement
class ConfigEditor(QObject):
    cfgChanged = Signal()

    def __init__(self):
        super().__init__()
        self.yaml = YAML()
        self.yaml.preserve_quotes = True
        self.yaml.default_flow_style = False
        self.yaml.indent(mapping=2, sequence=4, offset=2)

        self.nvr_cfg_dict = {}
        self.extern_cfg_dict = {}
        self.action_delay_cfg_dict = {}
        self.sync_cfg_dict = {}
        self.mcc_cfg_dict = {}
        self.ws_cfg_dict = {}
        self.finger_cfg_dict = {}
        self.lang_cfg_dict = {}
        self.front_lang_cfg_dict = {}

    def read_nvr_cfg(self):
        try:
            with open(nvr_cfg_path, mode='r', encoding="UTF-8") as f:
                self.nvr_cfg_dict = self.yaml.load(f)
                enabled = self.nvr_cfg_dict.get("nvr").get("enabled")
                server_ip = self.nvr_cfg_dict.get("nvr").get("device").get("hc-net").get("server-ip")
                username = self.nvr_cfg_dict.get("nvr").get("device").get("hc-net").get("username")
                password = self.nvr_cfg_dict.get("nvr").get("device").get("hc-net").get("password")
                enabled_upload = self.nvr_cfg_dict.get("nvr").get("video").get("enabled-upload")
                upload_save_dir = self.nvr_cfg_dict.get("nvr").get("video").get("upload-save-dir")
                product_channels = self.nvr_cfg_dict.get("nvr").get("device").get("hc-net").get("productChannels")
                # [{}] 形式嵌套传递到 QML 解析存在问题，换用 [[]] 形式嵌套
                product_channels_list = []
                for i in product_channels:
                    product_channels_list.append([i.get("productNo"), i.get("channel")])

        except Exception as err:
            logger.info(f"Yaml doesn't exist or structure is not standard. {err}")

        else:
            return {
                "enabled": enabled,
                "server_ip": server_ip,
                "username": username,
                "password": password,
                "enabled_upload": enabled_upload,
                "upload_save_dir": upload_save_dir,
                "product_channels": product_channels_list
            }

    nvr_config = Property(dict, read_nvr_cfg, notify=cfgChanged)

    @Slot(bool, str, str, str, bool, str, list)
    def save_nvr_cfg(self, enabled, server_ip, username, password, enabled_upload, upload_save_dir, channels):
        try:
            logger.info(f"Try to save configs to yaml")
            with open(nvr_cfg_path, mode='w', encoding="UTF-8") as f:
                self.nvr_cfg_dict["nvr"]["enabled"] = enabled
                self.nvr_cfg_dict["nvr"]["device"]["hc-net"]["server-ip"] = server_ip
                self.nvr_cfg_dict["nvr"]["device"]["hc-net"]["username"] = username
                self.nvr_cfg_dict["nvr"]["device"]["hc-net"]["password"] = password
                self.nvr_cfg_dict["nvr"]["video"]["enabled-upload"] = enabled_upload
                self.nvr_cfg_dict["nvr"]["video"]["upload-save-dir"] = upload_save_dir
                product_channels = []
                for i in channels:
                    product_channels.append({"productNo": i[0], "channel": i[1]})
                self.nvr_cfg_dict["nvr"]["device"]["hc-net"]["productChannels"] = product_channels
                self.yaml.dump(self.nvr_cfg_dict, f)

        except Exception as err:
            logger.error(err, exc_info=True)

    def read_extern_cfg(self):
        try:
            with open(extern_cfg_path, mode='r', encoding="UTF-8") as f:
                self.extern_cfg_dict = self.yaml.load(f)
                if product_type == 0:
                    if self.extern_cfg_dict.get("rodin") is not None:
                        reader_enabled = self.extern_cfg_dict.get("rodin").get("server").get("enabled")
                        readers = self.extern_cfg_dict.get("rodin").get("server").get("readers")
                        readers_list = []
                        for reader in readers:
                            readers_list.append([reader.get("cabinet-id"), reader.get("host"), str(reader.get("antennaNos", []))])
                        return {
                            "enabled": reader_enabled,
                            "readers": readers_list
                        }

                elif product_type == 1:
                    zaz_enabled = self.extern_cfg_dict.get("serial").get("finger").get("zaz").get("enabled")
                    zaz0a0_enabled = self.extern_cfg_dict.get("serial").get("finger").get("zaz0a0").get("enabled")
                    legacy_enabled = self.extern_cfg_dict.get("serial").get("finger").get("legacy").get("enabled")
                    idx = [zaz_enabled, zaz0a0_enabled, legacy_enabled].index(True)
                    baud_no = self.extern_cfg_dict.get("serial").get("finger").get("zaz").get("baud-no")
                    match_threshold = self.extern_cfg_dict.get("serial").get("finger").get("match-threshold")
                    return {
                        "device_type": idx,
                        "baud_no": baud_no - 1,
                        "match_threshold": match_threshold
                    }

                elif product_type == 2:
                    if self.extern_cfg_dict.get("honglu").get("serial") is not None:
                        enabled = self.extern_cfg_dict.get("honglu").get("serial").get("enabled")
                        port = self.extern_cfg_dict.get("honglu").get("serial").get("port")
                        baud_rate = self.extern_cfg_dict.get("honglu").get("serial").get("baud")
                        antenna_nos = self.extern_cfg_dict.get("honglu").get("serial").get("antenna-nos")
                        return {
                            "enabled": enabled,
                            "port": port,
                            "baud_rate": baud_rate,
                            "antenna_nos": str(antenna_nos)
                        }

        except Exception as err:
            logger.info(f"Yaml doesn't exist or structure is not standard. {err}")

    extern_config = Property(dict, read_extern_cfg, notify=cfgChanged)

    @Slot(int, int, int)
    def save_drug_extern_cfg(self, device_type, baud_no, match_threshold):
        try:
            logger.info(f"Try to save configs to yaml")
            with open(extern_cfg_path, mode='w', encoding="UTF-8") as f:
                if device_type == 0:
                    self.extern_cfg_dict["serial"]["finger"]["zaz"]["enabled"] = True
                    self.extern_cfg_dict["serial"]["finger"]["zaz0a0"]["enabled"] = False
                    self.extern_cfg_dict["serial"]["finger"]["legacy"]["enabled"] = False
                elif device_type == 1:
                    self.extern_cfg_dict["serial"]["finger"]["zaz0a0"]["enabled"] = True
                    self.extern_cfg_dict["serial"]["finger"]["zaz"]["enabled"] = False
                    self.extern_cfg_dict["serial"]["finger"]["legacy"]["enabled"] = False
                elif device_type == 2:
                    self.extern_cfg_dict["serial"]["finger"]["legacy"]["enabled"] = True
                    self.extern_cfg_dict["serial"]["finger"]["zaz"]["enabled"] = False
                    self.extern_cfg_dict["serial"]["finger"]["zaz0a0"]["enabled"] = False

                self.extern_cfg_dict["serial"]["finger"]["zaz"]["baud-no"] = baud_no
                self.extern_cfg_dict["serial"]["finger"]["match-threshold"] = match_threshold
                self.yaml.dump(self.extern_cfg_dict, f)

        except Exception as err:
            logger.error(err, exc_info=True)

    @Slot(bool, list)
    def save_consumable_extern_cfg(self, enabled, readers):
        try:
            logger.info(f"Try to save configs to yaml")
            with open(extern_cfg_path, mode='w', encoding="UTF-8") as f:
                if self.extern_cfg_dict.get("rodin") is not None:
                    self.extern_cfg_dict["rodin"]["server"]["enabled"] = enabled
                    readers_list = []
                    for i in readers:
                        cabinet_id = i[0]
                        host = i[1]
                        if i[2] is not None:
                            antenna_nos = eval(i[2])
                            readers_list.append({"antennaNos": antenna_nos, "cabinet-id": cabinet_id, "host": host, "port": 4001})
                        else:
                            readers_list.append({"cabinet-id": cabinet_id, "host": host, "port": 4001})
                    self.extern_cfg_dict["rodin"]["server"]["readers"] = readers_list
                self.yaml.dump(self.extern_cfg_dict, f)

        except Exception as err:
            logger.error(err, exc_info=True)

    @Slot(bool, str, int, str)
    def save_ecart_extern_cfg(self, enable, port, baud_rate, antenna_nos):
        try:
            logger.info(f"Try to save configs to yaml")
            with open(extern_cfg_path, mode='w', encoding="UTF-8") as f:
                self.extern_cfg_dict["honglu"]["serial"]["enabled"] = enable
                self.extern_cfg_dict["honglu"]["serial"]["port"] = port
                self.extern_cfg_dict["honglu"]["serial"]["baud"] = baud_rate
                self.extern_cfg_dict["honglu"]["serial"]["antenna-nos"] = eval(antenna_nos)
                self.yaml.dump(self.extern_cfg_dict, f)

        except Exception as err:
            logger.error(err, exc_info=True)

    def read_action_delay_cfg(self):
        try:
            with open(action_delay_cfg_path, mode='r', encoding="UTF-8") as f:
                self.action_delay_cfg_dict = self.yaml.load(f)
                delay_millis = self.action_delay_cfg_dict.get("actions").get("delay").get("delay-millis")
                delay_lock = self.action_delay_cfg_dict.get("actions").get("delay").get("delay-lock")
                time_out_no_lock = self.action_delay_cfg_dict.get("actions").get("delay").get("time-out-no-lock")

        except Exception as err:
            logger.info(f"Yaml doesn't exist or structure is not standard. {err}")

        else:
            return {
                "delay_millis": delay_millis,
                "delay_lock": delay_lock,
                "time_out_no_lock": time_out_no_lock
            }

    action_delay_config = Property(dict, read_action_delay_cfg, notify=cfgChanged)

    @Slot(int, int, int)
    def save_action_delay_cfg(self, delay_millis, delay_lock, time_out_no_lock):
        try:
            logger.info(f"Try to save configs to yaml")
            with open(action_delay_cfg_path, mode='w', encoding="UTF-8") as f:
                self.action_delay_cfg_dict["actions"]["delay"]["delay-millis"] = delay_millis
                self.action_delay_cfg_dict["actions"]["delay"]["delay-lock"] = delay_lock
                self.action_delay_cfg_dict["actions"]["delay"]["time-out-no-lock"] = time_out_no_lock
                self.yaml.dump(self.action_delay_cfg_dict, f)

        except Exception as err:
            logger.error(err, exc_info=True)

    def read_sync_cfg(self):
        try:
            with open(sync_cfg_path, mode='r', encoding="UTF-8") as f:
                self.sync_cfg_dict = self.yaml.load(f)
                host = self.sync_cfg_dict.get("sync").get("server").get("host")

        except Exception as err:
            logger.info(f"Yaml doesn't exist or structure is not standard. {err}")

        else:
            return {"host": host}

    sync_config = Property(dict, read_sync_cfg, notify=cfgChanged)

    @Slot(str)
    def save_sync_cfg(self, host):
        try:
            logger.info(f"Try to save configs to yaml")
            with open(sync_cfg_path, mode='w', encoding="UTF-8") as f:
                self.sync_cfg_dict["sync"]["server"]["host"] = host
                self.yaml.dump(self.sync_cfg_dict, f)

        except Exception as err:
            logger.error(err, exc_info=True)

    def read_mcc_cfg(self):
        try:
            with open(mcc_cfg_path, mode='r', encoding="UTF-8") as f:
                self.mcc_cfg_dict = self.yaml.load(f)
                enable = self.mcc_cfg_dict.get("mcc").get("enable")
                host = self.mcc_cfg_dict.get("mcc").get("hub").get("host")

        except Exception as err:
            logger.info(f"Yaml doesn't exist or structure is not standard. {err}")

        else:
            return {"enable": enable, "host": host}

    mcc_config = Property(dict, read_mcc_cfg, notify=cfgChanged)

    @Slot(bool, str)
    def save_mcc_cfg(self, enable, host):
        try:
            logger.info(f"Try to save configs to yaml")
            with open(mcc_cfg_path, mode='w', encoding="UTF-8") as f:
                self.mcc_cfg_dict["mcc"]["enable"] = enable
                self.mcc_cfg_dict["mcc"]["hub"]["host"] = host
                self.yaml.dump(self.mcc_cfg_dict, f)

        except Exception as err:
            logger.error(err, exc_info=True)

    def read_ws_cfg(self):
        try:
            with open(ws_cfg_path, mode='r', encoding="UTF-8") as f:
                self.ws_cfg_dict = self.yaml.load(f)
                restructure = self.ws_cfg_dict.get("protocol").get("restructure")

        except Exception as err:
            logger.info(f"Yaml doesn't exist or structure is not standard. {err}")

        else:
            return {"restructure": restructure}

    ws_config = Property(dict, read_ws_cfg, notify=cfgChanged)

    @Slot(bool)
    def save_ws_cfg(self, restructure):
        try:
            logger.info(f"Try to save configs to yaml")
            with open(ws_cfg_path, mode='w', encoding="UTF-8") as f:
                self.ws_cfg_dict["protocol"]["restructure"] = restructure
                self.yaml.dump(self.ws_cfg_dict, f)

        except Exception as err:
            logger.error(err, exc_info=True)

    def read_finger_cfg(self):
        try:
            with open(finger_cfg_path, mode='r', encoding="UTF-8") as f:
                self.finger_cfg_dict = self.yaml.load(f)
                port = self.finger_cfg_dict.get("serial").get("finger").get("zaz0a0").get("port").split("/")[-1]
                baud_rate = self.finger_cfg_dict.get("serial").get("finger").get("zaz0a0").get("baut")

        except Exception as err:
            logger.info(f"Yaml doesn't exist or structure is not standard. {err}")

        else:
            return {
                "port": port,
                "baud_rate": baud_rate
            }

    finger_config = Property(dict, read_finger_cfg, notify=cfgChanged)

    @Slot(str, int)
    def save_finger_cfg(self, port, baud_rate):
        try:
            logger.info(f"Try to save configs to yaml")
            with open(finger_cfg_path, mode='w', encoding="UTF-8") as f:
                self.finger_cfg_dict["serial"]["finger"]["zaz0a0"]["port"] = "/dev/" + port
                self.finger_cfg_dict["serial"]["finger"]["zaz0a0"]["baut"] = baud_rate
                self.yaml.dump(self.finger_cfg_dict, f)

        except Exception as err:
            logger.error(err, exc_info=True)

    def read_lang_cfg(self):
        try:
            with open(lang_cfg_path, mode='r', encoding="UTF-8") as f:
                self.lang_cfg_dict = self.yaml.load(f)
                lang = self.lang_cfg_dict.get("i18n").get("language")

            with open("/nubomed/NbClient-linux-x64/resources/static/config.json", mode="r", encoding="UTF-8") as f:
                self.front_lang_cfg_dict = json.load(f)
                front_lang = self.front_lang_cfg_dict.get("language")

        except Exception as err:
            logger.info(f"Yaml doesn't exist or structure is not standard. {err}")

        else:
            return {
                "lang": lang,
                "front_lang": front_lang
            }

    lang_config = Property(dict, read_lang_cfg, notify=cfgChanged)

    @Slot(str, str)
    def save_lang_cfg(self, lang, front_lang):
        try:
            logger.info(f"Try to save configs to yaml")
            with open(lang_cfg_path, mode='w', encoding="UTF-8") as f:
                self.lang_cfg_dict["i18n"]["language"] = lang
                self.yaml.dump(self.lang_cfg_dict, f)

            with open("/nubomed/NbClient-linux-x64/resources/static/config.json", mode='w', encoding="UTF-8") as f:
                self.front_lang_cfg_dict["language"] = front_lang
                json.dump(self.front_lang_cfg_dict, f)

        except Exception as err:
            logger.error(err, exc_info=True)
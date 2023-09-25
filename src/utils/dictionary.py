from PySide6.QtCore import QLocale


locale = QLocale.system().name()

if locale == "zh_CN":
    # 指昂方形指纹模块返回码字典
    code_dict = {
        0: "执行成功",
        1: "数据包接收错误",
        2: "传感器上没有手指",
        3: "录入指纹图象失败",
        4: "指纹太淡",
        5: "指纹太糊",
        6: "指纹太乱",
        7: "指纹特征点太少",
        8: "指纹不匹配",
        9: "没搜索到指纹",
        10: "特征合并失败",
        11: "地址号超出指纹库范围",
        12: "从指纹库读模板出错",
        13: "上传特征失败",
        14: "模块不能接收后续数据包",
        15: "上传图象失败",
        16: "删除模板失败",
        17: "清空指纹库失败",
        18: "不能进入休眠",
        19: "口令不正确",
        20: "系统复位失败",
        21: "无效指纹图象",
        -1: "发送失败",
        -2: "接收失败"
    }

    # 指昂圆形指纹模块返回码字典
    new_code_dict = {
        0: "处理成功",
        1: "处理失败",
        16: "与指定编号中模板的1:1比对失败",
        17: "已进行1:N比对，但相同模板不存在",
        18: "在指定编号中不存在已注册的模板",
        19: "在指定编号中已存在模板",
        20: "不存在已注册的模板",
        21: "不存在可注册的模板ID",
        22: "不存在已损坏的模板",
        23: "指定的模板数据无效",
        24: "该指纹已注册",
        25: "指纹图像质量不好",
        26: "模板合成失败",
        27: "没有进行通讯密码确认",
        28: "外部Flash烧写出错",
        29: "指定模板编号无效",
        34: "使用了不正确的参数",
        35: "超时，没有输入指纹",
        37: "指纹合成个数无效",
        38: "Buffer ID值不正确",
        40: "采集器上没有指纹输入",
        65: "指令被取消",
        -1: "发送失败"
    }

    # 串口板设备类型字典
    device_dict = {
        "0708": "身份RFID读卡器类",
        "0107": "条码扫描头类",
        "020a": "人体感应类"
    }

elif locale in ["zh_TW", "zh_HK", "zh_MO"]:
    code_dict = {
        0: "執行成功",
        1: "數據包接收錯誤",
        2: "傳感器上沒有手指",
        3: "錄入指紋圖象失敗",
        4: "指紋太淡",
        5: "指紋太糊",
        6: "指紋太亂",
        7: "指紋特征點太少",
        8: "指紋不匹配",
        9: "沒搜索到指紋",
        10: "特征合並失敗",
        11: "地址號超出指紋庫範圍",
        12: "從指紋庫讀模板出錯",
        13: "上傳特征失敗",
        14: "模塊不能接收後續數據包",
        15: "上傳圖象失敗",
        16: "刪除模板失敗",
        17: "清空指紋庫失敗",
        18: "不能進入休眠",
        19: "口令不正確",
        20: "系統復位失敗",
        21: "無效指紋圖象",
        -1: "發送失敗",
        -2: "接收失敗"
    }

    new_code_dict = {
        0: "處理成功",
        1: "處理失敗",
        16: "與指定編號中模板的1:1比對失敗",
        17: "已進行1:N比對，但相同模板不存在",
        18: "在指定編號中不存在已註冊的模板",
        19: "在指定編號中已存在模板",
        20: "不存在已註冊的模板",
        21: "不存在可註冊的模板ID",
        22: "不存在已損壞的模板",
        23: "指定的模板數據無效",
        24: "該指紋已註冊",
        25: "指紋圖像質量不好",
        26: "模板合成失敗",
        27: "沒有進行通訊密碼確認",
        28: "外部Flash燒寫出錯",
        29: "指定模板編號無效",
        34: "使用了不正確的參數",
        35: "超時，沒有輸入指紋",
        37: "指紋合成個數無效",
        38: "Buffer ID值不正確",
        40: "采集器上沒有指紋輸入",
        65: "指令被取消",
        -1: "發送失敗"
    }

    device_dict = {
        "0708": "身份RFID讀卡器類",
        "0107": "條碼掃描頭類",
        "020a": "人體感應類"
    }

else:
    code_dict = {
        0: "Executed Successfully",
        1: "Data pacakge error",
        2: "No finger on the sensor",
        3: "Collect fingerprint image failed",
        4: "Fingerprint is too unclear",
        5: "Fingerprint is too blurry",
        6: "Fingerprint is too messy",
        7: "Fingerprint is lack of features",
        8: "Fingerprint mismatched",
        9: "Fingerprint is not found",
        10: "Features merge failed",
        11: "The number is out of database",
        12: "Get fingerprint from database failed",
        13: "Upload feature failed",
        14: "Module can't receive subsequent data package",
        15: "Upload image failed",
        16: "Delete fingerprint failed",
        17: "Clear fingerprint database failed",
        18: "Can't enter sleep mode",
        19: "Incorrect password",
        20: "Reset system failed",
        21: "Invalid fingerprint image",
        -1: "Send failed",
        -2: "Receive failed"
    }

    new_code_dict = {
        0: "Process successfully",
        1: "Process failed",
        16: "1:1 match fingerprint with specified template failed",
        17: "1:N comparison has been conducted, but there are no matching template",
        18: "There is no registered template within the specified number",
        19: "Template already exists within the specified range",
        20: "There is no registered template",
        21: "There is no template ID that can be registered",
        22: "There is no corrupted template",
        23: "The specified template data is invalid",
        24: "The fingerprint is already registered",
        25: "Fingerprint image quality is poor",
        26: "Merge Template failed",
        27: "Communication password confirmation is not conducted",
        28: "Burn external flash error",
        29: "The specified template number is invalid",
        34: "Incorrect parameters are used",
        35: "Timeout, no fingerprint input",
        37: "The number of combined fingerprints is invalid",
        38: "Buffer ID value is incorrect",
        40: "There is no fingerprint input on the sensor",
        65: "Instruction is cancelled",
        -1: "Send failed"
    }

    device_dict = {
        "0708": "RFID reader",
        "0107": "Code scanner",
        "020a": "Human presence sensor"
    }

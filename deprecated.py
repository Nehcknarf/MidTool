class TreeItem:
    def __init__(self, parent: "TreeItem" = None):
        self._parent = parent
        self._key = ""
        self._value = ""
        self._value_type = None
        self._comment = ""
        self._children = []

    def appendChild(self, item: "TreeItem"):
        """Add item as a child"""
        self._children.append(item)

    def child(self, row: int) -> "TreeItem":
        """Return the child of the current item from the given row"""
        return self._children[row]

    def parent(self) -> "TreeItem":
        """Return the parent of the current item"""
        return self._parent

    def childCount(self) -> int:
        """Return the number of children of the current item"""
        return len(self._children)

    def row(self) -> int:
        """Return the row where the current item occupies in the parent"""
        return self._parent._children.index(self) if self._parent else 0

    # def columnCount(self) -> int:
    #     """Return the number of columns"""
    #     return 3

    def insertChild(self, position: int, count: int, parent: QModelIndex = QModelIndex()) -> bool:
        if position < 0 or position > len(self._children):
            return False

        for row in range(count):
            item = TreeItem(parent)
            self._children.insert(position, item)
        return True

    def removeChildren(self, position: int, count: int) -> bool:
        if position < 0 or position + count > len(self._children):
            return False

        for row in range(count):
            self._children.pop(position)

        return True

    @property
    def key(self) -> str:
        """Return the key name"""
        return self._key

    @key.setter
    def key(self, key: str):
        """Set key name of the current item"""
        self._key = key

    @property
    def value(self) -> str:
        """Return the value name of the current item"""
        return self._value

    @value.setter
    def value(self, value: str):
        """Set value name of the current item"""
        self._value = value

    @property
    def value_type(self):
        """Return the python type of the item's value."""
        return self._value_type

    @value_type.setter
    def value_type(self, value):
        """Set the python type of the item's value."""
        self._value_type = value

    @property
    def comment(self) -> str:
        """Return the comment name of the current item"""
        return self._comment

    @comment.setter
    def comment(self, value: str):
        """Set comment name of the current item"""
        self._comment = value

    @classmethod
    def load(cls, value: Union[List, Dict], parent: "TreeItem" = None, sort=False) -> "TreeItem":
        rootItem = TreeItem(parent)
        rootItem.key = "root"

        if isinstance(value, dict):
            items = sorted(value.items()) if sort else value.items()
            comment = value.ca.items
            for key, value in items:
                child = cls.load(value, rootItem)
                child.key = key
                child.value_type = type(value)
                try:
                    child.comment = [i.value.strip('# \n') for i in comment.get(key, []) if i is not None]
                except AttributeError:
                    child.comment = ""
                rootItem.appendChild(child)

        elif isinstance(value, list):
            for index, value in enumerate(value):
                child = cls.load(value, rootItem)
                child.key = index
                child.value_type = type(value)
                rootItem.appendChild(child)

        else:
            rootItem.value = (float(value) if isinstance(value, float) else value)
            rootItem.value_type = type(value)

        return rootItem


class JsonModel(QAbstractItemModel):
    def __init__(self, parent: QObject = None):
        super().__init__(parent)

        self._rootItem = TreeItem()
        self._headers = ("键", "值", "备注")

    def clear(self):
        """ Clear data from the model """
        self.load({})

    def load(self, document: dict):
        """ Load model from a nested dictionary """
        assert isinstance(
            document, (dict, list, tuple)
        ), "`document` must be of dict, list or tuple, " f"not {type(document)}"

        self.beginResetModel()

        self._rootItem = TreeItem.load(document)
        self._rootItem.value_type = type(document)

        self.endResetModel()

        return True

    def data(self, index: QModelIndex, role: Qt.ItemDataRole) -> Any:
        if not index.isValid():
            return None

        item = index.internalPointer()

        if role == Qt.DisplayRole or role == Qt.EditRole:
            if index.column() == 0:
                return item.key

            if index.column() == 1:
                return item.value

            if index.column() == 2:
                return item.comment

    def setData(self, index: QModelIndex, value: Any, role: Qt.ItemDataRole):
        item = index.internalPointer()

        if role == Qt.EditRole:
            if index.column() == 0:
                item.key = value
                self.dataChanged.emit(index, index, [Qt.EditRole])
                return True
            elif index.column() == 1:
                item.value = value
                item.value_type = type(value)
                self.dataChanged.emit(index, index, [Qt.EditRole])
                return True
            # elif index.column() == 2:
            #     item.comment = value
            #     self.dataChanged.emit(index, index, [Qt.EditRole])
            #     return True
        return False

    def headerData(self, section: int, orientation: Qt.Orientation, role: Qt.ItemDataRole):
        if role != Qt.DisplayRole:
            return None

        if orientation == Qt.Horizontal:
            return self._headers[section]

    def index(self, row: int, column: int, parent=QModelIndex()) -> QModelIndex:
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            parentItem = self._rootItem
        else:
            parentItem = parent.internalPointer()

        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QModelIndex()

    def parent(self, index: QModelIndex()) -> QModelIndex:
        if not index.isValid():
            return QModelIndex()

        childItem = index.internalPointer()
        parentItem = childItem.parent()

        if parentItem == self._rootItem:
            return QModelIndex()

        return self.createIndex(parentItem.row(), 0, parentItem)

    def rowCount(self, parent=QModelIndex()):
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parentItem = self._rootItem
        else:
            parentItem = parent.internalPointer()

        return parentItem.childCount()

    def columnCount(self, parent=QModelIndex()):
        return 3

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        flags = super(JsonModel, self).flags(index)

        if index.column() == 1 or index.column() == 0:
            return Qt.ItemIsEditable | flags
        else:
            return flags

    def get_item(self, index: QModelIndex = QModelIndex()) -> TreeItem:
        if index.isValid():
            item = index.internalPointer()
            if item:
                return item

        return self._rootItem

    def insertRows(self, position: int, rows: int, parent: QModelIndex = QModelIndex()) -> bool:
        parent_item = self.get_item(parent)
        if not parent_item:
            return False

        self.beginInsertRows(parent, position, position + rows - 1)
        success = parent_item.insertChild(position, rows, parent)
        self.endInsertRows()

        return success

    def removeRows(self, position: int, rows: int, parent: QModelIndex = QModelIndex()) -> bool:
        parent_item: TreeItem = self.get_item(parent)
        if not parent_item:
            return False

        self.beginRemoveRows(parent, position, position + rows - 1)
        success = parent_item.removeChildren(position, rows)
        self.endRemoveRows()

        return success

    def to_yaml(self, item=None):
        if item is None:
            item = self._rootItem

        nchild = item.childCount()

        if item.value_type is comments.CommentedMap:
            document = comments.CommentedMap()
            for i in range(nchild):
                ch = item.child(i)
                document[ch.key] = self.to_yaml(ch)
                try:
                    document.yaml_add_eol_comment(ch.comment[0], ch.key)
                except IndexError:
                    pass
            return document

        elif item.value_type is comments.CommentedSeq or item.value_type is None:
            document = comments.CommentedSeq()
            for i in range(nchild):
                ch = item.child(i)
                document.append(self.to_yaml(ch))
            return document

        else:
            if isinstance(item.value, item.value_type):
                return item.value
            else:
                return eval(str(item.value))


class MySortFilterProxyModel(QSortFilterProxyModel):
    def __init__(self):
        super().__init__()
        self.key = ''

    def setFilterKey(self, key):
        self.key = key
        self.invalidateFilter()
        TabWidget.treeView_2.expandAll()

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        index = self.sourceModel().index(source_row, 0, source_parent)

        if self.key in str(index.data(Qt.DisplayRole)):
            return True
        else:
            for i in range(self.sourceModel().rowCount(index)):
                if self.filterAcceptsRow(i, index):
                    return True
            return False


class ConfigEditor2(QWidget):
    def __init__(self):
        super().__init__()
        self.yaml = YAML()
        self.yaml.preserve_quotes = True
        self.yaml.default_flow_style = False
        self.yaml.indent(mapping=2, sequence=4, offset=2)

        self.path = ''
        self.document = {}

        self.model = JsonModel()
        self.proxy_model = MySortFilterProxyModel()
        self.proxy_model.setSourceModel(self.model)
        TabWidget.treeView_2.setModel(self.proxy_model)

        selection_model = TabWidget.treeView_2.selectionModel()
        selection_model.selectionChanged.connect(self.update_actions)

        # TabWidget.treeView_2.setSortingEnabled(True)
        TabWidget.treeView_2.header().setSectionResizeMode(0, QHeaderView.Stretch)
        TabWidget.treeView_2.header().setSectionResizeMode(1, QHeaderView.Stretch)
        TabWidget.treeView_2.setAlternatingRowColors(True)
        # TabWidget.treeView_2.setSelectionBehavior(QAbstractItemView.SelectItems)

        TabWidget.openButton.clicked.connect(self.open_dir)
        TabWidget.savecfgButton.clicked.connect(self.save_cfg)
        TabWidget.comboBox.currentTextChanged.connect(self.read_cfg)
        TabWidget.lineEdit_filter.textChanged.connect(self.proxy_model.setFilterKey)
        TabWidget.insert_row_button.clicked.connect(self.insert_row)
        TabWidget.remove_row_button.clicked.connect(self.remove_row)
        TabWidget.insert_child_button.clicked.connect(self.insert_child)


    def open_dir(self):
        self.path = QFileDialog.getExistingDirectory(self, "打开文件夹", "/home", QFileDialog.ShowDirsOnly)
        if self.path:
            TabWidget.comboBox.clear()
            TabWidget.comboBox.addItems([f for f in os.listdir(self.path) if f.endswith('yml')])

    def read_cfg(self):
        file_name = TabWidget.comboBox.currentText()
        with open(f"{self.path}/{file_name}", mode='r', encoding="UTF-8") as f:
            # TODO 判断文件类型
            self.document = self.yaml.load(f)
            self.model.load(self.document)
            TabWidget.treeView_2.expandAll()

    def save_cfg(self):
        with open(f"{self.path}/{TabWidget.comboBox.currentText()}", mode='w', encoding="UTF-8") as f:
            doc = self.model.to_yaml()
            self.document.update(doc)
            self.yaml.dump(self.document, f)

    def update_actions(self):
        selection_model = TabWidget.treeView_2.selectionModel()
        has_selection = not selection_model.selection().isEmpty()
        TabWidget.remove_row_button.setEnabled(has_selection)

        current_index = selection_model.currentIndex()
        has_current = current_index.isValid()
        TabWidget.insert_row_button.setEnabled(has_current)

        if has_current:
            TabWidget.treeView_2.closePersistentEditor(current_index)

    def insert_child(self):
        selection_model = TabWidget.treeView_2.selectionModel()
        index = selection_model.currentIndex()
        model = TabWidget.treeView_2.model()

        if not model.insertRow(0, index):
            return

        child = model.index(0, 0, index)
        model.setData(child, "请填写", Qt.EditRole)

        selection_model.setCurrentIndex(model.index(0, 0, index), QItemSelectionModel.ClearAndSelect)
        self.update_actions()

    def insert_row(self):
        index = TabWidget.treeView_2.selectionModel().currentIndex()
        model = TabWidget.treeView_2.model()
        parent = index.parent()

        if not model.insertRow(index.row() + 1, parent):
            return

        self.update_actions()

        for column in range(model.columnCount(parent)):
            child = model.index(index.row() + 1, column, parent)
            model.setData(child, "请填写", Qt.EditRole)

    def remove_row(self):
        index = TabWidget.treeView_2.selectionModel().currentIndex()
        model = TabWidget.treeView_2.model()

        if model.removeRow(index.row(), index.parent()):
            self.update_actions()


class Reader(QRunnable):
    def __init__(self, path, chunk=524288):  # 512KB
        super().__init__()
        self.signals = WorkerSignals()
        self.path = path
        self.chunk = chunk

    def run(self):
        file = QFile(self.path)
        if not file.open(QIODevice.ReadOnly | QIODevice.Text):
            return
        file.seek(file.size() - self.chunk)
        # while not file.atEnd():
        #     QApplication.processEvents()
        # mem = file.map(-1, self.pos)
        # file.unmap(mem)
        log = bytes(file.readAll()).decode('utf8')
        self.signals.context.emit(log)
        file.close()


class LogBrowser(QWidget):
    def __init__(self):
        super().__init__()
        self.q = deque()
        self.keyword_len = 0
        self.thread = None
        # UI
        TabWidget.textBrowser.ensureCursorVisible()
        TabWidget.textBrowser.document().setMaximumBlockCount(500)
        TabWidget.StartDateEdit.setMinimumDate(QDate.currentDate().addDays(-7))
        TabWidget.EndDateEdit.setMinimumDate(QDate.currentDate().addDays(-7))
        TabWidget.StartDateEdit.setMaximumDate(QDate.currentDate().addDays(-1))
        TabWidget.EndDateEdit.setMaximumDate(QDate.currentDate().addDays(-1))
        TabWidget.StartDateEdit.setDate(QDate.currentDate().addDays(-1))
        TabWidget.EndDateEdit.setDate(QDate.currentDate().addDays(-1))

        TabWidget.openfileButton.clicked.connect(self.open_log)
        TabWidget.tailButton.clicked.connect(self.tail_log)
        TabWidget.stoptailButton.clicked.connect(self.kill_tail)
        TabWidget.clearButton.clicked.connect(TabWidget.lineEdit.clear)
        TabWidget.searchButton.clicked.connect(self.search)
        TabWidget.prevButton.clicked.connect(self.prev)
        TabWidget.nextButton.clicked.connect(self.next)
        # TabWidget.lineEdit.textChanged.connect(self.search)
        TabWidget.match_case.stateChanged.connect(self.search)
        TabWidget.match_word.stateChanged.connect(self.search)
        # TabWidget.textBrowser.verticalScrollBar().valueChanged.connect(self.auto_load)
        # TabWidget.StartDateEdit.dateChanged.connect(self.date_valid_checker)
        TabWidget.EndDateEdit.dateChanged.connect(self.date_valid_checker)
        TabWidget.downlogButton.clicked.connect(self.download_log)

    def auto_load(self):
        v_value = TabWidget.textBrowser.verticalScrollBar().value()
        if v_value < 100:
            TabWidget.textBrowser.moveCursor(QTextCursor.Start)
            # TabWidget.textBrowser.insertPlainText("test")

    def open_log(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择日志文件", TabWidget.logpathlineEdit.text(), "日志文件 (*.log)")
        if path:
            TabWidget.textBrowser.clear()
            self.thread = Reader(path)
            self.thread.signals.context.connect(TabWidget.textBrowser.append, Qt.BlockingQueuedConnection)
            # self.thread_read.context.connect(TabWidget.textBrowser.setText)
            threadpool.start(self.thread)

    def tail_log(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择待监控的日志文件", TabWidget.logpathlineEdit.text(), "日志文件 (*.log)")
        if path:
            TabWidget.textBrowser.clear()
            if system == "Windows":
                self.thread = Commander(f"powershell Get-Content {path} -tail 30 -Wait")
            elif system == "Linux":
                self.thread = Commander(f"tail -f -n 30 {path}")
            self.thread.signals.stdout.connect(TabWidget.textBrowser.append)
            threadpool.start(self.thread)

    def kill_tail(self):
        if self.thread.isRunning():
            self.thread.requestInterruption()
            self.thread.quit()
            self.thread.wait()
        self.thread.deleteLater()
        TabWidget.textBrowser.append("终止命令执行成功，线程释放")

    def highlight(self, pos):
        cursor = TabWidget.textBrowser.textCursor()
        cursor.setPosition(pos)
        cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, self.keyword_len)
        # Set the visible cursor
        TabWidget.textBrowser.setTextCursor(cursor)

    def prev(self):
        pos = self.q.pop()
        self.q.appendleft(pos)
        self.highlight(pos)

    def next(self):
        pos = self.q.popleft()
        self.q.append(pos)
        self.highlight(pos)

    def search(self):
        keyword = TabWidget.lineEdit.text()
        self.keyword_len = len(keyword)
        if not keyword:
            return
        context = TabWidget.textBrowser.toPlainText()
        # 恢复默认的颜色
        cursor = TabWidget.textBrowser.textCursor()
        cursor.select(QTextCursor.Document)
        cursor.setCharFormat(QTextCharFormat())
        cursor.clearSelection()
        TabWidget.textBrowser.setTextCursor(cursor)
        TabWidget.textBrowser.moveCursor(QTextCursor.Start)

        fmt = QTextCharFormat()
        fmt.setBackground(QColor.fromRgbF(1.000000, 1.000000, 0.000000, 1.000000))

        if TabWidget.match_case.isChecked():
            match_case = Qt.CaseSensitive
        else:
            match_case = Qt.CaseInsensitive

        if TabWidget.match_word.isChecked():
            keyword = f"\\b{keyword}\\b"

        self.q.clear()
        # Returns the position of the first match, or -1 if there was no match.
        rx = QRegExp(keyword, match_case)
        pos = rx.indexIn(context, 0)
        if pos != -1:
            self.q.append(pos)
        while pos != -1:
            QApplication.processEvents()
            cursor.setPosition(pos)
            cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, self.keyword_len)
            cursor.mergeCharFormat(fmt)
            pos += rx.matchedLength()
            pos = rx.indexIn(context, pos)
            if pos != -1:
                self.q.append(pos)

        TabWidget.label.setText(f"找到{len(self.q)}处")

    @staticmethod
    def date_valid_checker():
        start_date = TabWidget.StartDateEdit.date()
        end_date = TabWidget.EndDateEdit.date()
        if end_date < start_date:
            TabWidget.EndDateEdit.setDate(start_date)

    def download_log(self):
        start_date = TabWidget.StartDateEdit.date()
        end_date = TabWidget.EndDateEdit.date()
        diff = start_date.daysTo(end_date) + 1
        date_list = [end_date.addDays(-i).toString("yyyy-MM-dd") for i in range(diff)]
        path = QFileDialog.getExistingDirectory(self, "保存到文件夹", "/media", QFileDialog.ShowDirsOnly)
        time = datetime.now()
        if path:
            with ZipFile(f"{path}/log-save-{time.strftime('%Y%m%d%H%M%S%f')[:-3]}.zip", 'a') as myzip:
                for date in date_list:
                    myzip.write(f"/nubomed/consumable-cabinet-service/logs/mid-{date}-1.log.gz")
            TabWidget.textBrowser.append("压缩完成并拷贝到指定目录！")


class FileManager(QWidget):
    def __init__(self):
        super().__init__()
        self.model_index = QModelIndex()
        self.model = QFileSystemModel()
        self.model.setRootPath("/media")
        self.model.setReadOnly(False)

        TabWidget.treeView.setModel(self.model)
        TabWidget.treeView.setRootIndex(self.model.index("/nubomed"))
        TabWidget.treeView.setColumnWidth(0, 200)
        TabWidget.treeView.setIconSize(QSize(30, 30))

        TabWidget.treeView_driver.setModel(self.model)
        TabWidget.treeView_driver.setRootIndex(self.model.index("/media"))
        TabWidget.treeView_driver.setColumnWidth(0, 200)
        TabWidget.treeView_driver.setIconSize(QSize(30, 30))

        TabWidget.treeView.clicked.connect(self.left)
        TabWidget.treeView_driver.clicked.connect(self.right)
        TabWidget.pushButton_open.clicked.connect(self.open)
        TabWidget.pushButton_mkdir.clicked.connect(self.mkdir)
        TabWidget.pushButton_remove.clicked.connect(self.rm)
        # TabWidget.pushButton_copy.clicked.connect()

    def left(self, index):
        TabWidget.treeView_driver.clearSelection()
        self.path = self.model.filePath(index)

    def right(self, index):
        TabWidget.treeView.clearSelection()
        self.path = self.model.filePath(index)

    def popup(self):
        msg_box = QMessageBox()
        msg_box.setWindowTitle("错误")
        msg_box.setText("文件已经存在")
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.exec()

    def open(self):
        path = QFileDialog.getExistingDirectory(self, "打开文件夹", "/home", QFileDialog.ShowDirsOnly)
        if path:
            TabWidget.treeView.setRootIndex(self.model.index(path))

    def mkdir(self):
        dir_name, _ = QInputDialog.getText(self, "新建文件夹", "请输入文件夹名称", QLineEdit.Normal, "")
        if dir_name:
            self.model.mkdir(self.model_index.parent(), dir_name)

    def rm(self):
        self.model.remove(self.model_index)


class DeviceAliveCheck(QWidget):
    def __init__(self):
        super().__init__()
        self.ws = QWebSocket()

        self.ws.connected.connect(self.connected)
        self.ws.disconnected.connect(self.disconnected)
        self.ws.textMessageReceived.connect(self.recv)

        TabWidget.textBrowser_ws.document().setMaximumBlockCount(500)
        TabWidget.pushButton_openWs.clicked.connect(self.open)
        TabWidget.pushButton_closeWs.clicked.connect(self.close)
        TabWidget.pushButton_checkAlive.clicked.connect(self.send)
        TabWidget.pushButton_clear.clicked.connect(TabWidget.textBrowser_ws.clear)

    def open(self):
        TabWidget.textBrowser_ws.append('建立 WebSocket 连接...')
        self.ws.open(QUrl("ws://127.0.0.1:8080/websocket"))

    def close(self):
        TabWidget.textBrowser_ws.append('关闭 WebSocket 连接...')
        self.ws.abort()

    def send(self):
        device_type = TabWidget.comboBox_wsDevice.currentText()
        time = datetime.now()

        if device_type == "查询柜锁状态" or device_type ==  "查詢櫃鎖狀態":
            request_json = {
                "requestId": f"GetCabinetLockStatus-{time.strftime('%Y%m%d%H%M%S%f')[:-3]}",
                "cmd": "GetCabinetLockStatus",
                "seq": 1,
                "ackSeq": 0,
                "params": {
                    "device": f"{TabWidget.comboBox_deviceList.currentText()}"
                }
            }
        elif device_type == "查询柜门状态" or device_type == "查詢櫃門狀態":
            request_json = {
                "requestId": f"GetCabinetDoorStatus-{time.strftime('%Y%m%d%H%M%S%f')[:-3]}",
                "cmd": "GetCabinetDoorStatus",
                "seq": 1,
                "ackSeq": 0,
                "params": {
                    "device": f"{TabWidget.comboBox_deviceList.currentText()}"
                }
            }
        elif device_type == "开始消毒" or device_type == "開始消毒":
            request_json = {
                "requestId": f"StartSterilize-{time.strftime('%Y%m%d%H%M%S%f')[:-3]}",
                "cmd": "StartSterilize",
                "seq": 1,
                "ackSeq": 0,
                "params": {
                    "device": f"{TabWidget.comboBox_deviceList.currentText()}"
                }
            }
        elif device_type == "停止消毒" or device_type == "停止消毒":
            request_json = {
                "requestId": f"StopSterilize-{time.strftime('%Y%m%d%H%M%S%f')[:-3]}",
                "cmd": "StopSterilize",
                "seq": 1,
                "ackSeq": 0,
                "params": {
                    "device": f"{TabWidget.comboBox_deviceList.currentText()}"
                }
            }
        request = json.dumps(request_json)
        ret = self.ws.sendTextMessage(request)
        TabWidget.textBrowser_ws.append(f'已发送请求：{request}，共{ret}比特')

    def connected(self):
        TabWidget.textBrowser_ws.append('WebSocket 连接已建立')
        TabWidget.pushButton_openWs.setEnabled(False)
        time = datetime.now()
        request_json = {
            "requestId": f"GetAllCabinetInfo-{time.strftime('%Y%m%d%H%M%S%f')[:-3]}",
            "cmd": "GetAllCabinetInfo",
            "seq": 1,
            "ackSeq": 0
        }
        request = json.dumps(request_json)
        ret = self.ws.sendTextMessage(request)

    def disconnected(self):
        TabWidget.textBrowser_ws.append('WebSocket 连接已断开')
        TabWidget.comboBox_deviceList.clear()
        TabWidget.pushButton_openWs.setEnabled(True)

    def recv(self, message):
        status_dict = {0: '关闭', 1: '打开'}
        msg = json.loads(message)
        TabWidget.textBrowser_ws.append(f'接收响应：{str(msg)}')
        cmd_type = msg.get("cmd")
        if cmd_type == 'GetAllCabinetInfoResult':
            device_list = msg.get('params').get('devices')
            TabWidget.comboBox_deviceList.addItems(device_list)
        elif cmd_type == 'GetCabinetLockStatusResult':
            lock_status = msg.get('params').get('lockStatus')
            lock_status = status_dict.get(lock_status)
            TabWidget.textBrowser_ws.append(f'锁状态：{lock_status}')
        elif cmd_type == 'GetCabinetDoorStatusResult':
            door_status = msg.get('params').get('doorStatus')
            door_status = status_dict.get(door_status)
            TabWidget.textBrowser_ws.append(f'门状态：{door_status}')
        elif cmd_type == 'ReportTemperature' or 'ReportHumidity':
            temperature = msg.get('params').get('temperature')
            if temperature:
                TabWidget.textBrowser_ws.append(f'温度：{temperature}')
            humidity = msg.get('params').get('humidity')
            if humidity:
                TabWidget.textBrowser_ws.append(f'湿度：{humidity}')
        elif cmd_type == 'NotifyUVLampStatusChanged':
            uv_lamp_status = msg.get('params').get('uvLampStatus')
            uv_lamp_status = status_dict.get(uv_lamp_status)
            TabWidget.textBrowser_ws.append(f'紫外灯状态：{uv_lamp_status}')


class Commander(QThread):
    stdout = Signal(str)
    verbose = Signal(str)

    def __init__(self, command, password=None, wd="/nubomed"):
        super().__init__()
        self.command = command
        self.password = password
        self.wd = wd

    def run(self):
        process_command = QProcess()
        process_command.setProcessChannelMode(QProcess.MergedChannels)
        if self.command.__contains__("sudo"):
            # Pipe
            process_echo = QProcess()
            process_echo.setStandardOutputProcess(process_command)
            process_echo.setProgram("echo")
            process_echo.setArguments(self.password)
            process_echo.start()
            # process_echo.start(f"echo {self.password}")
            process_echo.waitForFinished()

        if system == "Linux":
            process_command.setWorkingDirectory(self.wd)
        process_command.setProgram(self.command.split()[0])
        process_command.setArguments(self.command.split()[1:])
        process_command.start()
        # process_command.start(self.command)
        process_command.waitForStarted()
        string = ""
        while process_command.state() != QProcess.NotRunning:
            QApplication.processEvents()
            if QThread.currentThread().isInterruptionRequested():
                break
            if process_command.waitForReadyRead():
                if system == "Windows":
                    stdout = bytes(process_command.readAllStandardOutput()).decode("gbk").rstrip('\r\n')
                elif system == "Linux":
                    stdout = bytes(process_command.readAllStandardOutput()).decode("utf8").rstrip('\n')
                self.stdout.emit(stdout)
                string += f"{stdout}\n"

        self.verbose.emit(string)
        self.stdout.emit("指令已执行")

import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import Controls as MyControls

import src.editor


Item {
    MyControls.VertTabBar {
        id: vertTabBarConfig
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.top: parent.top
        width: 180

        MyControls.TabButton {
            anchors.left: parent.left
            anchors.right: parent.right
            text: qsTr("NVR")
        }

        MyControls.TabButton {
            anchors.left: parent.left
            anchors.right: parent.right
            text: qsTr("Reader")
        }

        MyControls.TabButton {
            anchors.left: parent.left
            anchors.right: parent.right
            text: qsTr("Sync")
        }

        MyControls.TabButton {
            anchors.left: parent.left
            anchors.right: parent.right
            text: qsTr("MCC")
        }
    }

    ConfigEditor {
        id: configEditor
        property var nvr_cfg: configEditor.nvr_config
        property var extern_cfg: configEditor.extern_config
        property var sync_cfg: configEditor.sync_config
        property var mcc_cfg: configEditor.mcc_config
    }

    StackLayout {
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 16
        anchors.left: parent.left
        anchors.leftMargin: 196
        anchors.right: parent.right
        anchors.rightMargin: 16
        anchors.top: parent.top
        anchors.topMargin: 16
        currentIndex: vertTabBarConfig.currentIndex

        MyControls.GroupBox {
            id: groupBoxNvr
            Layout.fillHeight: true
            Layout.fillWidth: true

            Label {
                font.family: bold.name
                font.pixelSize: 16
                text: qsTr("Network Video Recorder")
            }

            MyControls.Button {
                anchors.right: parent.right
                anchors.top: parent.top
                text: qsTr("Save")
                onClicked: {
                    let productChannels = []
                    for (let i = 0; i < columnLayoutProductChannel.children.length; ++i) {
                        productChannels.push([columnLayoutProductChannel.children[i].productNo, columnLayoutProductChannel.children[i].channel])
                    }
                    configEditor.save_nvr_cfg(
                        switchNvrEnabled.checked,
                        textFieldNvrServerIp.text,
                        textFieldNvrUserName.text,
                        textFieldNvrPassword.text,
                        switchNvrEnabledUpload.checked,
                        textFieldNvrUploadSaveDir.text,
                        productChannels)
                }
            }

            GridLayout {
                anchors.left: parent.left
                anchors.leftMargin: 50
                anchors.top: parent.top
                anchors.topMargin: 54
                columns: 2
                rowSpacing: 20
                rows: 10

                Label {
                    font.family: bold.name
                    font.pixelSize: 16
                    text: qsTr("Enabled NVR")
                }

                MyControls.Switch {
                    id: switchNvrEnabled
                    checked: configEditor.nvr_cfg["enabled"] === undefined ? 0 : configEditor.nvr_cfg["enabled"]
                }

                Label {
                    font.family: bold.name
                    font.pixelSize: 16
                    text: qsTr("Host")
                }

                MyControls.TextField {
                    id: textFieldNvrServerIp
                    implicitWidth: 150
                    text: configEditor.nvr_cfg["server_ip"] === undefined ? null : configEditor.nvr_cfg["server_ip"]
                    inputMethodHints: Qt.ImhDigitsOnly
                    validator: RegularExpressionValidator {
                        regularExpression: /((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})(\.((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})){3}/
                    }
                }

                Label {
                    font.family: bold.name
                    font.pixelSize: 16
                    text: qsTr("Username")
                }

                MyControls.TextField {
                    id: textFieldNvrUserName
                    implicitWidth: 150
                    text: configEditor.nvr_cfg["username"] === undefined ? null : configEditor.nvr_cfg["username"]
                    inputMethodHints: Qt.ImhPreferLowercase
                }

                Label {
                    font.family: bold.name
                    font.pixelSize: 16
                    text: qsTr("Password")
                }

                MyControls.TextField {
                    id: textFieldNvrPassword
                    implicitWidth: 150
                    text: configEditor.nvr_cfg["password"] === undefined ? null : configEditor.nvr_cfg["password"]
                    inputMethodHints: Qt.ImhPreferLowercase
                }

                Label {
                    font.family: bold.name
                    font.pixelSize: 16
                    text: qsTr("Enabled Video Upload")
                }

                MyControls.Switch {
                    id: switchNvrEnabledUpload
                    checked: configEditor.nvr_cfg["enabled_upload"] === undefined ? 0 : configEditor.nvr_cfg["enabled_upload"]
                }

                Label {
                    font.family: bold.name
                    font.pixelSize: 16
                    text: qsTr("Sever video storage path")
                }

                MyControls.TextField {
                    id: textFieldNvrUploadSaveDir
                    implicitWidth: 250
                    text: configEditor.nvr_cfg["upload_save_dir"] === undefined ? null : configEditor.nvr_cfg["upload_save_dir"]
                    inputMethodHints: Qt.ImhUrlCharactersOnly
                }
            }

            ColumnLayout {
                id: columnLayoutProductChannelFixPart
                anchors.left: parent.left
                anchors.leftMargin: 600
                anchors.top: parent.top
                anchors.topMargin: 54
                spacing: 20

                RowLayout {
                    Label {
                        font.family: bold.name
                        font.pixelSize: 16
                        text: qsTr("Product Channel Configuration")
                    }

                    MyControls.Button {
                        implicitWidth: 40
                        text: qsTr("+")
                        onClicked: {
                            let component = Qt.createComponent("qrc:/content/ObjectProductChannel.qml")
                            component.createObject(columnLayoutProductChannel)
                        }
                    }
                }
            }

            ScrollView {
                anchors.left: parent.left
                anchors.leftMargin: 600
                anchors.top: columnLayoutProductChannelFixPart.bottom
                anchors.topMargin: 20
                width: columnLayoutProductChannel.width + 10
                height: 400

                ColumnLayout {
                    id: columnLayoutProductChannel
                    spacing: 20
                    Component.onCompleted: {
                        let productChannels = configEditor.nvr_cfg["product_channels"]
                        if (productChannels !== undefined) {
                            let component = Qt.createComponent("qrc:/content/ObjectProductChannel.qml")
                            for (const i of productChannels) {
                                component.createObject(columnLayoutProductChannel, {"productNo": i[0], "channel": i[1]})
                            }
                        }
                    }
                }
            }
        }

        MyControls.GroupBox {
            Layout.fillHeight: true
            Layout.fillWidth: true

            Label {
                font.family: bold.name
                font.pixelSize: 16
                text: qsTr("Reader")
            }

            MyControls.Button {
                anchors.right: parent.right
                anchors.top: parent.top
                text: qsTr("Save")
                onClicked: {
                    let readers = []
                    for (let i = 0; i < columnLayoutReader.children.length; ++i) {
                        readers.push([columnLayoutReader.children[i].cabinetId, columnLayoutReader.children[i].host, columnLayoutReader.children[i].antennaNo])
                    }
                    configEditor.save_consumable_extern_cfg(switchReaderEnabled.checked, readers)
                }
            }

            ColumnLayout {
                id: columnLayoutReaderFixPart
                anchors.left: parent.left
                anchors.leftMargin: 50
                anchors.top: parent.top
                anchors.topMargin: 54
                spacing: 20

                RowLayout {
                    Label {
                        font.family: bold.name
                        font.pixelSize: 16
                        text: qsTr("Enabled Reader")
                    }

                    MyControls.Switch {
                        id: switchReaderEnabled
                        checked: configEditor.extern_cfg["enabled"] === undefined ? 0 : configEditor.extern_cfg["enabled"]
                    }
                }

                RowLayout {
                    Label {
                        font.family: bold.name
                        font.pixelSize: 16
                        text: qsTr("Multi-Reader Configuration")
                    }

                    MyControls.Button {
                        implicitWidth: 40
                        text: qsTr("+")
                        onClicked: {
                            let component = Qt.createComponent("qrc:/content/ObjectReader.qml")
                            component.createObject(columnLayoutReader)
                        }
                    }
                }
            }

            ScrollView {
                anchors.left: parent.left
                anchors.leftMargin: 50
                anchors.top: columnLayoutReaderFixPart.bottom
                anchors.topMargin: 20
                width: columnLayoutReader.width + 10
                height: 350

                ColumnLayout {
                    id: columnLayoutReader
                    spacing: 20
                    Component.onCompleted: {
                        let readers = configEditor.extern_cfg["readers"]
                        if (readers !== undefined) {
                            let component = Qt.createComponent("qrc:/content/ObjectReader.qml")
                            for (const i of readers) {
                                component.createObject(columnLayoutReader, {"cabinetId": i[0], "host": i[1], "antennaNo": i[2]})
                            }
                        }
                    }
                }
            }
        }

        MyControls.GroupBox {
            Layout.fillHeight: true
            Layout.fillWidth: true

            Label {
                font.family: bold.name
                font.pixelSize: 16
                text: qsTr("Synchronization")
            }

            MyControls.Button {
                anchors.right: parent.right
                anchors.top: parent.top
                text: qsTr("Save")
                onClicked: {
                    configEditor.save_sync_cfg(textFieldSyncHost.text)
                }
            }

            GridLayout {
                anchors.left: parent.left
                anchors.leftMargin: 50
                anchors.top: parent.top
                anchors.topMargin: 54
                columns: 2
                rowSpacing: 20
                rows: 10

                Label {
                    font.family: bold.name
                    font.pixelSize: 16
                    text: qsTr("Synchronized Host IP")
                }

                MyControls.TextField {
                    id: textFieldSyncHost
                    implicitWidth: 150
                    text: configEditor.sync_cfg["host"] === undefined ? null : configEditor.sync_cfg["host"]
                    inputMethodHints: Qt.ImhDigitsOnly
                    validator: RegularExpressionValidator {
                        regularExpression: /((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})(\.((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})){3}/
                    }
                }
            }
        }

        MyControls.GroupBox {
            Layout.fillHeight: true
            Layout.fillWidth: true

            Label {
                font.family: bold.name
                font.pixelSize: 16
                text: qsTr("Middleware Control Center")
            }

            MyControls.Button {
                anchors.right: parent.right
                anchors.top: parent.top
                text: qsTr("Save")
                onClicked: {
                    configEditor.save_mcc_cfg(textFieldMccEnable.checked, textFieldMccHost.text)
                }
            }

            GridLayout {
                anchors.left: parent.left
                anchors.leftMargin: 50
                anchors.top: parent.top
                anchors.topMargin: 54
                columns: 2
                rowSpacing: 20
                rows: 10

                Label {
                    font.family: bold.name
                    font.pixelSize: 16
                    text: qsTr("Connect to MCC at starting")
                }

                MyControls.Switch {
                    id: textFieldMccEnable
                    checked: configEditor.mcc_cfg["enable"] === undefined ? 0 : configEditor.mcc_cfg["enable"]
                }

                Label {
                    font.family: bold.name
                    font.pixelSize: 16
                    text: qsTr("MCC Host IP")
                }

                MyControls.TextField {
                    id: textFieldMccHost
                    implicitWidth: 150
                    text: configEditor.mcc_cfg["host"] === undefined ? null : configEditor.mcc_cfg["host"]
                    inputMethodHints: Qt.ImhDigitsOnly
                    validator: RegularExpressionValidator {
                        regularExpression: /((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})(\.((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})){3}/
                    }
                }
            }
        }
    }
}

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
            text: qsTr("Fingerprint")
        }

        MyControls.TabButton {
            anchors.left: parent.left
            anchors.right: parent.right
            text: qsTr("Action Delay")
        }

        MyControls.TabButton {
            anchors.left: parent.left
            anchors.right: parent.right
            text: qsTr("Sync/MCC/WS")
        }
    }

    ConfigEditor {
        id: configEditor
        property var nvr_cfg: configEditor.nvr_config
        property var extern_cfg: configEditor.extern_config
        property var action_delay_cfg: configEditor.action_delay_config
        property var sync_cfg: configEditor.sync_config
        property var mcc_cfg: configEditor.mcc_config
        property var ws_cfg: configEditor.ws_config
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
                text: qsTr("Fingerprint")
            }

            MyControls.Button {
                anchors.right: parent.right
                anchors.top: parent.top
                text: qsTr("Save")
                onClicked: {
                    configEditor.save_drug_extern_cfg(comboBoxFingerprintDeviceType.currentIndex, comboBoxFingerprintBaudRate.currentText, textFieldFingerprintMatchingThreshold.text)
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
                    text: qsTr("Device Type")
                }

                MyControls.ComboBox {
                    id: comboBoxFingerprintDeviceType
                    currentIndex: configEditor.extern_cfg["device_type"] === undefined ? -1 : configEditor.extern_cfg["device_type"]
                    implicitWidth: 200
                    model: [qsTr("Square Fingerprint"), qsTr("Round Fingerprint"), qsTr("Optical Fingerprint")]
                }

                Label {
                    font.family: bold.name
                    font.pixelSize: 16
                    text: qsTr("Square Fingerprint baud rate")
                }

                MyControls.ComboBox {
                    id: comboBoxFingerprintBaudRate
                    currentIndex: configEditor.extern_cfg["baud_no"] === undefined ? -1 : configEditor.extern_cfg["baud_no"]
                    implicitWidth: 100
                    model: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
                }

                Label {
                    font.family: bold.name
                    font.pixelSize: 16
                    text: qsTr("Fingerprint matching threshold")
                }

                MyControls.TextField {
                    id: textFieldFingerprintMatchingThreshold
                    implicitWidth: 100
                    text: configEditor.extern_cfg["match_threshold"] === undefined ? null : configEditor.extern_cfg["match_threshold"]
                    // validator: IntValidator {
                    //     bottom: 0
                    //     top: 100
                    // }
                    validator: RegularExpressionValidator {
                        regularExpression: /^([1-9][0-9]{0,1}|100)$/
                    }
                    inputMethodHints: Qt.ImhDigitsOnly
                }
            }
        }

        MyControls.GroupBox {
            Layout.fillHeight: true
            Layout.fillWidth: true

            Label {
                font.family: bold.name
                font.pixelSize: 16
                text: qsTr("Action Delay")
            }

            MyControls.Button {
                anchors.right: parent.right
                anchors.top: parent.top
                text: qsTr("Save")
                onClicked: {
                    configEditor.save_action_delay_cfg(textFieldActionDelayMillis.text, textFieldActionDelayLock.text, textFieldActionDelayTimeOut.text)
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
                    text: qsTr("Interval between command (ms)")
                }

                MyControls.TextField {
                    id: textFieldActionDelayMillis
                    implicitWidth: 70
                    text: configEditor.action_delay_cfg["delay_millis"] === undefined ? null : configEditor.action_delay_cfg["delay_millis"]
                    inputMethodHints: Qt.ImhDigitsOnly
                }

                Label {
                    font.family: bold.name
                    font.pixelSize: 16
                    text: qsTr("Batch unlock delay (ms)")
                }

                MyControls.TextField {
                    id: textFieldActionDelayLock
                    implicitWidth: 70
                    text: configEditor.action_delay_cfg["delay_lock"] === undefined ? null : configEditor.action_delay_cfg["delay_lock"]
                    inputMethodHints: Qt.ImhDigitsOnly
                }

                Label {
                    font.family: bold.name
                    font.pixelSize: 16
                    text: qsTr("Unclosed drawer check interval (ms)")
                }

                MyControls.TextField {
                    id: textFieldActionDelayTimeOut
                    implicitWidth: 70
                    text: configEditor.action_delay_cfg["time_out_no_lock"] === undefined ? null : configEditor.action_delay_cfg["time_out_no_lock"]
                    inputMethodHints: Qt.ImhDigitsOnly
                }
            }
        }

        MyControls.GroupBox {
            Layout.fillHeight: true
            Layout.fillWidth: true

            Label {
                font.family: bold.name
                font.pixelSize: 16
                text: qsTr("Synchronization/Middleware Control Center/WebSocket")
            }

            MyControls.Button {
                anchors.right: parent.right
                anchors.top: parent.top
                text: qsTr("Save")
                onClicked: {
                    configEditor.save_sync_cfg(textFieldSyncHost.text)
                    configEditor.save_mcc_cfg(textFieldMccEnable.checked, textFieldMccHost.text)
                    configEditor.save_ws_cfg(textFieldWsRestructure.checked)
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

                Label {
                    font.family: bold.name
                    font.pixelSize: 16
                    text: qsTr("WebSocket protocol restructure")
                }

                MyControls.Switch {
                    id: textFieldWsRestructure
                    checked: configEditor.ws_cfg["restructure"] === undefined ? 0 : configEditor.ws_cfg["restructure"]
                }
            }
        }
    }
}

import QtQuick 6.5
import QtQuick.Controls 6.5
import QtQuick.Layouts 6.5
import Controls as MyControls
import src.editor.drug

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

            property var objArr: []

            Label {
                font.bold: true
                font.pixelSize: 16
                text: qsTr("Network Video Recorder")
            }
            MyControls.Button {
                anchors.right: parent.right
                anchors.top: parent.top
                text: qsTr("Save")

                onClicked: {
                    for (const i of groupBoxNvr.objArr) {
                        console.log(i.productNo, i.channel)
                    }
                    configEditor.save_nvr_cfg(switchNvrEnabled.checked, textFieldNvrServerIp.text, textFieldNvrUserName.text, textFieldNvrPassword.text, switchNvrEnabledUpload.checked, textFieldNvrUploadSaveDir.text);
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
                    font.pixelSize: 16
                    text: qsTr("Enabled NVR")
                }
                MyControls.Switch {
                    id: switchNvrEnabled

                    checked: configEditor.nvr_cfg["enabled"] === undefined ? 0 : configEditor.nvr_cfg["enabled"]
                }
                Label {
                    font.pixelSize: 16
                    text: qsTr("Host")
                }
                MyControls.TextField {
                    id: textFieldNvrServerIp

                    implicitWidth: 200
                    text: configEditor.nvr_cfg["server_ip"] === undefined ? null : configEditor.nvr_cfg["server_ip"]
                    // validator: RegularExpressionValidator {
                    // regularExpression:
                    // }
                    inputMethodHints: Qt.ImhDigitsOnly
                }
                Label {
                    font.pixelSize: 16
                    text: qsTr("Username")
                }
                MyControls.TextField {
                    id: textFieldNvrUserName

                    implicitWidth: 200
                    text: configEditor.nvr_cfg["username"] === undefined ? null : configEditor.nvr_cfg["username"]
                }
                Label {
                    font.pixelSize: 16
                    text: qsTr("Password")
                }
                MyControls.TextField {
                    id: textFieldNvrPassword

                    implicitWidth: 200
                    text: configEditor.nvr_cfg["password"] === undefined ? null : configEditor.nvr_cfg["password"]
                }
                Label {
                    font.pixelSize: 16
                    text: qsTr("Enabled Video Upload")
                }
                MyControls.Switch {
                    id: switchNvrEnabledUpload

                    checked: configEditor.nvr_cfg["enabled_upload"] === undefined ? 0 : configEditor.nvr_cfg["enabled_upload"]
                }
                Label {
                    font.pixelSize: 16
                    text: qsTr("Sever video storage path")
                }
                MyControls.TextField {
                    id: textFieldNvrUploadSaveDir

                    implicitWidth: 250
                    text: configEditor.nvr_cfg["upload_save_dir"] === undefined ? null : configEditor.nvr_cfg["upload_save_dir"]
                }
            }
            ScrollView {
                height: 410
                width: 420

                anchors.right: parent.right
                anchors.rightMargin: 100
                anchors.top: parent.top
                anchors.topMargin: 54

                ColumnLayout {
                    id: columnLayoutProductChannel
                    anchors.fill: parent
                    spacing: 20

                    RowLayout {
                        Layout.alignment: Qt.AlignCenter | Qt.AlignVCenter
                        Label {
                            font.pixelSize: 16
                            text: qsTr("Product Channel Configuration")
                        }

                        MyControls.Button {
                            implicitWidth: 40
                            text: qsTr("+")
                            onClicked: {
                                let component = Qt.createComponent("ObjectProductChannel.qml")
                                let obj = component.createObject(columnLayoutProductChannel)
                            }
                        }
                    }

                    Component.onCompleted: {
                        let component = Qt.createComponent("ObjectProductChannel.qml")
                        for (const i of configEditor.nvr_cfg["product_channels"]) {
                            let obj = component.createObject(columnLayoutProductChannel, {
                                "productNo": i[0],
                                "channel": i[1]
                            })
                        }
                    }
                }
            }
        }

        MyControls.GroupBox {
            Layout.fillHeight: true
            Layout.fillWidth: true

            Label {
                font.bold: true
                font.pixelSize: 16
                text: qsTr("Fingerprint")
            }
            MyControls.Button {
                anchors.right: parent.right
                anchors.top: parent.top
                text: qsTr("Save")

                onClicked: {
                    configEditor.save_extern_cfg(comboBoxFingerprintDeviceType.currentIndex, comboBoxFingerprintBaudRate.currentText, textFieldFingerprintMatchingThreshold.text);
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
                    font.pixelSize: 16
                    text: qsTr("Fingerprint matching threshold")
                }
                MyControls.TextField {
                    id: textFieldFingerprintMatchingThreshold

                    implicitWidth: 100
                    text: configEditor.extern_cfg["match_threshold"] === undefined ? null : configEditor.extern_cfg["match_threshold"]

                    validator: IntValidator {
                        bottom: 0
                        top: 100
                    }

                    inputMethodHints: Qt.ImhDigitsOnly
                }
            }
        }
        MyControls.GroupBox {
            Layout.fillHeight: true
            Layout.fillWidth: true

            Label {
                font.bold: true
                font.pixelSize: 16
                text: qsTr("Action Delay")
            }
            MyControls.Button {
                anchors.right: parent.right
                anchors.top: parent.top
                text: qsTr("Save")

                onClicked: {
                    configEditor.save_action_delay_cfg(textFieldActionDelayMillis.text, textFieldActionDelayLock.text, textFieldActionDelayTimeOut.text);
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
                    font.pixelSize: 16
                    text: qsTr("Interval between command (ms)")
                }
                MyControls.TextField {
                    id: textFieldActionDelayMillis

                    implicitWidth: 100
                    text: configEditor.action_delay_cfg["delay_millis"] === undefined ? null : configEditor.action_delay_cfg["delay_millis"]
                    inputMethodHints: Qt.ImhDigitsOnly
                }
                Label {
                    font.pixelSize: 16
                    text: qsTr("Batch unlock delay (ms)")
                }
                MyControls.TextField {
                    id: textFieldActionDelayLock

                    implicitWidth: 100
                    text: configEditor.action_delay_cfg["delay_lock"] === undefined ? null : configEditor.action_delay_cfg["delay_lock"]
                    inputMethodHints: Qt.ImhDigitsOnly
                }
                Label {
                    font.pixelSize: 16
                    text: qsTr("Unclosed drawer check interval (ms)")
                }
                MyControls.TextField {
                    id: textFieldActionDelayTimeOut

                    implicitWidth: 100
                    text: configEditor.action_delay_cfg["time_out_no_lock"] === undefined ? null : configEditor.action_delay_cfg["time_out_no_lock"]
                    inputMethodHints: Qt.ImhDigitsOnly
                }
            }
        }
        MyControls.GroupBox {
            Layout.fillHeight: true
            Layout.fillWidth: true

            Label {
                font.bold: true
                font.pixelSize: 16
                text: qsTr("Synchronization/MCC/WebSocket")
            }
            MyControls.Button {
                anchors.right: parent.right
                anchors.top: parent.top
                text: qsTr("Save")

                onClicked: {
                    configEditor.save_sync_cfg(textFieldSyncHost.text);
                    configEditor.save_mcc_cfg(textFieldMccEnable.checked, textFieldMccHost.text);
                    configEditor.save_ws_cfg(textFieldWsRestructure.checked);
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
                    font.pixelSize: 16
                    text: qsTr("Synchronized Host IP")
                }
                MyControls.TextField {
                    id: textFieldSyncHost

                    implicitWidth: 200
                    text: configEditor.sync_cfg["host"] === undefined ? null : configEditor.sync_cfg["host"]
                    inputMethodHints: Qt.ImhDigitsOnly
                }
                Label {
                    font.pixelSize: 16
                    text: qsTr("Connect to MCC at starting")
                }
                MyControls.Switch {
                    id: textFieldMccEnable

                    checked: configEditor.mcc_cfg["enable"] === undefined ? 0 : configEditor.mcc_cfg["enable"]
                    implicitWidth: 200
                }
                Label {
                    font.pixelSize: 16
                    text: qsTr("MCC Host IP")
                }
                MyControls.TextField {
                    id: textFieldMccHost

                    implicitWidth: 200
                    text: configEditor.mcc_cfg["host"] === undefined ? null : configEditor.mcc_cfg["host"]
                    inputMethodHints: Qt.ImhDigitsOnly
                }
                Label {
                    font.pixelSize: 16
                    text: qsTr("WebSocket protocol restructure")
                }
                MyControls.Switch {
                    id: textFieldWsRestructure

                    checked: configEditor.ws_cfg["restructure"] === undefined ? 0 : configEditor.ws_cfg["restructure"]
                    implicitWidth: 200
                }
            }
        }
    }
}

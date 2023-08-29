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
            Layout.fillHeight: true
            Layout.fillWidth: true

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
                    configEditor.save_nvr_cfg(
                        switchNvrEnabled.checked,
                        textFieldNvrServerIp.text,
                        textFieldNvrUserName.text,
                        textFieldNvrPassword.text,
                        switchNvrEnabledUpload.checked,
                        textFieldNvrUploadSaveDir.text
                        )
                }
            }

            GridLayout {
                anchors.top: parent.top
                anchors.topMargin: 54
                anchors.left: parent.left
                anchors.leftMargin: 50
                rowSpacing: 20
                columns: 2
                rows: 10

                Label {
                    font.pixelSize: 16
                    text: qsTr("Enabled NVR")
                }
                MyControls.Switch {
                    id: switchNvrEnabled
                    checked: configEditor.nvr_cfg["enabled"]
                }

                Label {
                    font.pixelSize: 16
                    text: qsTr("Host")
                }
                MyControls.TextField {
                    id: textFieldNvrServerIp
                    implicitWidth: 200
                    text: configEditor.nvr_cfg["server_ip"]
                    // validator: RegularExpressionValidator {
                    // regularExpression:
                    // }
                }

                Label {
                    font.pixelSize: 16
                    text: qsTr("Username")
                }
                MyControls.TextField {
                    id: textFieldNvrUserName
                    implicitWidth: 200
                    text: configEditor.nvr_cfg["username"]
                }

                Label {
                    font.pixelSize: 16
                    text: qsTr("Password")
                }
                MyControls.TextField {
                    id: textFieldNvrPassword
                    implicitWidth: 200
                    text: configEditor.nvr_cfg["password"]
                }

                Label {
                    font.pixelSize: 16
                    text: qsTr("Enabled Video Upload")
                }
                MyControls.Switch {
                    id: switchNvrEnabledUpload
                    checked: configEditor.nvr_cfg["enabled_upload"]
                }

                Label {
                    font.pixelSize: 16
                    text: qsTr("Sever video storage path")
                }
                MyControls.TextField {
                    id: textFieldNvrUploadSaveDir
                    implicitWidth: 250
                    text: configEditor.nvr_cfg["upload_save_dir"]
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
                    configEditor.save_extern_cfg(
                        comboBoxFingerprintDeviceType.currentIndex,
                        comboBoxFingerprintBaudRate.currentText,
                        textFieldFingerprintMatchingThreshold.text
                        )
                }
            }

            GridLayout {
                anchors.top: parent.top
                anchors.topMargin: 54
                anchors.left: parent.left
                anchors.leftMargin: 50
                rowSpacing: 20
                columns: 2
                rows: 10

                Label {
                    font.pixelSize: 16
                    text: qsTr("Device Type")
                }
                MyControls.ComboBox {
                    id: comboBoxFingerprintDeviceType
                    implicitWidth: 200
                    model: [
                        qsTr("Square Fingerprint"),
                        qsTr("Round Fingerprint"),
                        qsTr("Optical Fingerprint")
                    ]
                    currentIndex: configEditor.extern_cfg["device_type"]
                }

                Label {
                    font.pixelSize: 16
                    text: qsTr("Square Fingerprint baud rate")
                }
                MyControls.ComboBox {
                    id: comboBoxFingerprintBaudRate
                    implicitWidth: 200
                    model: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
                    currentIndex: configEditor.extern_cfg["baud_no"]
                }

                Label {
                    font.pixelSize: 16
                    text: qsTr("Fingerprint matching threshold")
                }
                MyControls.TextField {
                    id: textFieldFingerprintMatchingThreshold
                    implicitWidth: 50
                    text: configEditor.extern_cfg["match_threshold"]
                    validator: IntValidator {bottom: 0; top: 100;}
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
                    configEditor.save_action_delay_cfg(
                        textFieldActionDelayMillis.text,
                        textFieldActionDelayLock.text,
                        textFieldActionDelayTimeOut.text
                        )
                }
            }

            GridLayout {
                anchors.top: parent.top
                anchors.topMargin: 54
                anchors.left: parent.left
                anchors.leftMargin: 50
                rowSpacing: 20
                columns: 2
                rows: 10

                Label {
                    font.pixelSize: 16
                    text: qsTr("Interval between command (ms)")
                }
                MyControls.TextField {
                    id: textFieldActionDelayMillis
                    implicitWidth: 100
                    text: configEditor.action_delay_cfg["delay_millis"]
                }

                Label {
                    font.pixelSize: 16
                    text: qsTr("Batch unlock delay (ms)")
                }
                MyControls.TextField {
                    id: textFieldActionDelayLock
                    implicitWidth: 100
                    text: configEditor.action_delay_cfg["delay_lock"]
                }

                Label {
                    font.pixelSize: 16
                    text: qsTr("Unclosed drawer check interval (ms)")
                }
                MyControls.TextField {
                    id: textFieldActionDelayTimeOut
                    implicitWidth: 100
                    text: configEditor.action_delay_cfg["time_out_no_lock"]
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
                    configEditor.save_sync_cfg(textFieldSyncHost.text)
                    configEditor.save_mcc_cfg(textFieldMccEnable.checked, textFieldMccHost.text)
                    configEditor.save_ws_cfg(textFieldWsRestructure.checked)
                }
            }

            GridLayout {
                anchors.top: parent.top
                anchors.topMargin: 54
                anchors.left: parent.left
                anchors.leftMargin: 50
                rowSpacing: 20
                columns: 2
                rows: 10

                Label {
                    font.pixelSize: 16
                    text: qsTr("Synchronized Host IP")
                }
                MyControls.TextField {
                    id: textFieldSyncHost
                    implicitWidth: 200
                    text: configEditor.sync_cfg["host"]
                }
                Label {
                    font.pixelSize: 16
                    text: qsTr("Connect to MCC at starting")
                }
                MyControls.Switch {
                    id: textFieldMccEnable
                    implicitWidth: 200
                    checked: configEditor.mcc_cfg["enable"]
                }
                Label {
                    font.pixelSize: 16
                    text: qsTr("MCC Host IP")
                }
                MyControls.TextField {
                    id: textFieldMccHost
                    implicitWidth: 200
                    text: configEditor.mcc_cfg["host"]
                }
                Label {
                    font.pixelSize: 16
                    text: qsTr("WebSocket protocol restructure")
                }
                MyControls.Switch {
                    id: textFieldWsRestructure
                    implicitWidth: 200
                    checked: configEditor.ws_cfg["restructure"]
                }
            }
        }
    }
}
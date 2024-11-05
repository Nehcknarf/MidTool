import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import Controls as MyControls

import src.editor
import src.serial


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
            text: qsTr("Reader")
        }

        MyControls.TabButton {
            anchors.left: parent.left
            anchors.right: parent.right
            text: qsTr("Fingerprint")
        }

        MyControls.TabButton {
            anchors.left: parent.left
            anchors.right: parent.right
            text: qsTr("Language")
        }
    }

    ConfigEditor {
        id: configEditor
        property var extern_cfg: configEditor.extern_config
        property var finger_cfg: configEditor.finger_config
        property var lang_cfg: configEditor.lang_config
    }

    Serial {
        id: serial
        property var ports: serial.availablePorts
        property var baud_rates: serial.baudRates
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
            id: groupBoxReader
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
                    configEditor.save_ecart_extern_cfg(
                        switchReaderEnabled.checked,
                        comboBoxReaderPort.currentText,
                        comboBoxReaderBaudRate.currentText,
                        textFieldReaderAntennaNo.text
                    )
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
                    text: qsTr("Enabled Reader")
                }

                MyControls.Switch {
                    id: switchReaderEnabled
                    checked: configEditor.extern_cfg["enabled"] === undefined ? 0 : configEditor.extern_cfg["enabled"]
                }

                Label {
                    font.family: bold.name
                    font.pixelSize: 16
                    text: qsTr("Serial Port")
                }

                MyControls.ComboBox {
                    id: comboBoxReaderPort
                    model: serial.ports
                    popup.onOpened: serial.update_ports()
                    Component.onCompleted: currentIndex = indexOfValue(configEditor.extern_cfg["port"] === undefined ? null : configEditor.extern_cfg["port"])
                }

                Label {
                    font.family: bold.name
                    font.pixelSize: 16
                    text: qsTr("Baud Rate")
                }

                MyControls.ComboBox {
                    id: comboBoxReaderBaudRate
                    model: serial.baud_rates
                    Component.onCompleted: currentIndex = indexOfValue(configEditor.extern_cfg["baud_rate"] === undefined ? null : configEditor.extern_cfg["baud_rate"])
                }

                Label {
                    font.family: bold.name
                    font.pixelSize: 16
                    text: qsTr("Antenna No. List")
                }

                MyControls.TextField {
                    id: textFieldReaderAntennaNo
                    implicitWidth: 200
                    text: configEditor.extern_cfg["antenna_nos"] === undefined ? null : configEditor.extern_cfg["antenna_nos"]
                    inputMethodHints: Qt.ImhPreferNumbers
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
                    configEditor.save_finger_cfg(
                        comboBoxFPPort.currentText,
                        comboBoxFPBaudRate.currentText
                    )
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
                    text: qsTr("Serial Port")
                }

                MyControls.ComboBox {
                    id: comboBoxFPPort
                    model: serial.ports
                    popup.onOpened: serial.update_ports()
                    Component.onCompleted: currentIndex = indexOfValue(configEditor.finger_cfg["port"] === undefined ? null : configEditor.finger_cfg["port"])
                }

                Label {
                    font.family: bold.name
                    font.pixelSize: 16
                    text: qsTr("Baud Rate")
                }

                MyControls.ComboBox {
                    id: comboBoxFPBaudRate
                    model: serial.baud_rates
                    Component.onCompleted: currentIndex = indexOfValue(configEditor.finger_cfg["baud_rate"] === undefined ? null : configEditor.finger_cfg["baud_rate"])
                }
            }
        }

        MyControls.GroupBox {
            Layout.fillHeight: true
            Layout.fillWidth: true

            Label {
                font.family: bold.name
                font.pixelSize: 16
                text: qsTr("Language (System needs to reboot for a language change to take effect.)")
            }

            MyControls.Button {
                anchors.right: parent.right
                anchors.top: parent.top
                text: qsTr("Save")
                onClicked: {
                    configEditor.save_lang_cfg(
                        comboBoxBELanguage.currentValue,
                        comboBoxFELanguage.currentValue
                    )
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
                    text: qsTr("Backend Language")
                }

                MyControls.ComboBox {
                    id: comboBoxBELanguage
                    model: [
                        {"value": "zh_CN", "text": qsTr("Simplified Chinese")},
                        {"value": "en_US", "text": qsTr("English")}
                    ]
                    textRole: "text"
                    valueRole: "value"
                    Component.onCompleted: currentIndex = indexOfValue(configEditor.lang_cfg["lang"] === undefined ? null : configEditor.lang_cfg["lang"])
                }

                Label {
                    font.family: bold.name
                    font.pixelSize: 16
                    text: qsTr("Frontend Language")
                }

                MyControls.ComboBox {
                    id: comboBoxFELanguage
                    model: [
                        {"value": "zh_cn", "text": qsTr("Simplified Chinese")},
                        {"value": "en_us", "text": qsTr("English")}
                    ]
                    textRole: "text"
                    valueRole: "value"
                    Component.onCompleted: currentIndex = indexOfValue(configEditor.lang_cfg["front_lang"] === undefined ? null : configEditor.lang_cfg["front_lang"])
                }
            }
        }
    }
}

import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import Controls as MyControls
import Components as MyComponents

import src.serial


Item {
    MyControls.GroupBox {
        id: groupBoxSerialConfig
        anchors.left: parent.left
        anchors.leftMargin: 16
        anchors.right: parent.right
        anchors.rightMargin: 16
        anchors.top: parent.top
        anchors.topMargin: 16
        height: 110

        Label {
            font.family: bold.name
            font.pixelSize: 16
            text: qsTr("Config")
        }

        Serial {
            id: serial
            Component.onCompleted: serial.pinout.connect(terminalOutputSer.textArea.append)
        }

        RowLayout {
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.verticalCenter: parent.verticalCenter

            Label {
                font.family: bold.name
                font.pixelSize: 16
                text: qsTr("Serial Port")
            }

            MyControls.ComboBox {
                id: comboBoxSerPort
                model: serial.availablePorts
                enabled: ! switchSer.checked
                // currentIndex: -1
                popup.onOpened: serial.update_ports()
            }

            Label {
                font.family: bold.name
                font.pixelSize: 16
                text: qsTr("Baud Rate")
            }

            MyControls.ComboBox {
                id: comboBoxSerBaudRate
                model: serial.baudRates
                enabled: ! switchSer.checked
                Component.onCompleted: currentIndex = indexOfValue(115200)
            }

            Label {
                font.family: bold.name
                font.pixelSize: 16
                text: qsTr("Connect")
            }

            MyControls.Switch {
                id: switchSer
                onCheckedChanged: {
                    checked ? serial.open_device(comboBoxSerPort.currentValue, comboBoxSerBaudRate.currentValue) : serial.close_device()
                }
            }
        }
    }

    MyComponents.TerminalOutput {
        id: terminalOutputSer
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 16
        anchors.left: parent.left
        anchors.leftMargin: 16
        anchors.right: parent.right
        anchors.rightMargin: 16
        anchors.top: groupBoxSerialConfig.bottom
        anchors.topMargin: 16
    }
}
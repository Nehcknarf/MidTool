import QtQuick 6.5
import QtQuick.Controls 6.5
import QtQuick.Layouts 6.5

import Controls as MyControls

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
            font.family: bold.font.family
            font.pixelSize: 16
            text: qsTr("Config")
        }
        Serial {
            id: serial
            Component.onCompleted: serial.Pinout.connect(textAreaSerial.append)
        }
        RowLayout {
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.verticalCenter: parent.verticalCenter

            Label {
                font.family: bold.font.family
                font.pixelSize: 16
                text: qsTr("Serial Port")
            }
            MyControls.ComboBox {
                id: comboBoxSerCom

                model: serial.coms
                // currentIndex: -1
            }
            Label {
                font.family: bold.font.family
                font.pixelSize: 16
                text: qsTr("Baud Rate")
            }
            MyControls.ComboBox {
                id: comboBoxSerBaudRate

                model: serial.baud_rates
            }
            Label {
                font.family: bold.font.family
                font.pixelSize: 16
                text: qsTr("Connect")
            }
            MyControls.Switch {
                onCheckedChanged: {
                    checked ? serial.open_device(comboBoxSerCom.currentValue, comboBoxSerBaudRate.currentValue) : serial.close_device();
                }
            }
        }
    }
    MyControls.GroupBox {
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 16
        anchors.left: parent.left
        anchors.leftMargin: 16
        anchors.right: parent.right
        anchors.rightMargin: 16
        anchors.top: groupBoxSerialConfig.bottom
        anchors.topMargin: 16

        Label {
            font.family: bold.font.family
            font.pixelSize: 16
            text: qsTr("Terminal Output")
        }
        MyControls.Button {
            anchors.right: parent.right
            anchors.top: parent.top
            text: qsTr("Clear")

            onClicked: textAreaSerial.clear()
        }
        ScrollView {
            anchors.bottom: parent.bottom
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.topMargin: 54

            background: Rectangle {
                border.color: "#CAD0E0"
                radius: 8
            }

            TextArea {
                id: textAreaSerial
                anchors.fill: parent
                font.family: medium.font.family
                font.pixelSize: 16
                readOnly: true
            }
        }
    }
}
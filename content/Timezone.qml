import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import Controls as MyControls
import Components as MyComponents

import src.time


MyControls.GroupBox {
    anchors.fill: parent
    anchors.margins: 16

    Label {
        font.family: bold.name
        font.pixelSize: 16
        text: qsTr("Settings")
    }

    TimeEditor {
        id: timeEditor
        // Component.onCompleted: timeEditor.Stdout.connect()
    }

    MyComponents.Dialog {
        id: dialogSetTz
        onAction: {
         timeEditor.set_timezone(comboBoxComTimezone.currentText, input)
        }
    }

    MyComponents.Dialog {
        id: dialogSetDateTime
        onAction: {
         timeEditor.set_time(textFieldDateTime.text, input)
        }
    }

    MyComponents.Dialog {
        id: dialogSetNTP
        onAction: {
         timeEditor.add_ntp_servers(textFieldNTP.text, input)
        }
    }

    GridLayout {
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenter: parent.verticalCenter
        columns: 3
        rows: 3

        Label {
            font.family: bold.name
            font.pixelSize: 16
            text: qsTr("Timezone")
        }

        MyControls.ComboBox {
            id: comboBoxComTimezone
            implicitWidth: 300
            model: timeEditor.timezones
            Component.onCompleted: currentIndex = indexOfValue("Asia/Shanghai")
        }

        MyControls.Button {
            text: qsTr("Set Timezone")
            onClicked: {
                dialogSetTz.open()
            }
        }

        Label {
            font.family: bold.name
            font.pixelSize: 16
            text: qsTr("DateTime")
        }

        MyControls.TextField {
            id: textFieldDateTime
            implicitWidth: 300
            placeholderText: "YYYY-MM-DD HH:MM:SS"
            text: new Date().toLocaleString(Qt.locale(), "yyyy-MM-dd hh:mm:ss")
            inputMethodHints: Qt.ImhPreferNumbers
            validator: RegularExpressionValidator {
                regularExpression: /^(19|20)\d\d-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01]) (0[0-9]|1[0-9]|2[0-3]):([0-5][0-9]):([0-5][0-9])$/
            }
        }

        MyControls.Button {
            text: qsTr("Set DateTime")
            onClicked: {
                dialogSetDateTime.open()
            }
        }

        Label {
            font.family: bold.name
            font.pixelSize: 16
            text: qsTr("NTP Servers")
        }

        MyControls.TextField {
            id: textFieldNTP
            implicitWidth: 300
            placeholderText: qsTr("Servers are separated by space")
            inputMethodHints: Qt.ImhPreferNumbers
        }

        MyControls.Button {
            text: qsTr("Set NTP Servers")
            onClicked: {
                dialogSetNTP.open()
            }
        }
    }
}
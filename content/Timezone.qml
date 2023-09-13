import QtQuick 6.5
import QtQuick.Controls 6.5
import QtQuick.Layouts 6.5
import QtQuick.Dialogs 6.5

import Controls as MyControls

import src.time


Item {
    StackLayout {
        anchors.left: parent.left
        anchors.leftMargin: 16
        anchors.right: parent.right
        anchors.rightMargin: 16
        anchors.top: parent.top
        anchors.topMargin: 16
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 16

        TimeEditor {
            id: timeEditor
            // Component.onCompleted: timeEditor.Stdout.connect()
        }

        MyControls.GroupBox {
            Layout.fillHeight: true
            Layout.fillWidth: true

            Label {
                font.family: bold.font.family
                font.pixelSize: 16
                text: qsTr("Settings")
            }

            GridLayout {
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.verticalCenter: parent.verticalCenter
                columns: 3
                rows: 3

                Label {
                    font.family: bold.font.family
                    font.pixelSize: 16
                    text: qsTr("Timezone")
                }

                MyControls.ComboBox {
                    id: comboBoxComTimezone
                    implicitWidth: 300
                    model: timeEditor.timezones
                    // currentIndex: -1
                }

                Dialog {
                     id: dialogSetTz
                     modal: true
                     standardButtons: Dialog.Ok | Dialog.Cancel
                     title: qsTr("Please input user password")

                     contentItem: Rectangle {
                         color: "#FFFFFF"
                         implicitHeight: 50
                         implicitWidth: 200

                         TextField {
                             id: textFieldPswSetTz
                             anchors.centerIn: parent
                             echoMode: TextInput.Password
                             placeholderText: qsTr("Input user password")
                             focus: true
                         }
                     }

                     onAccepted: {
                         if (textFieldPswSetTz.text) {
                             timeEditor.set_timezone(comboBoxComTimezone.currentText, textFieldPswSetTz.text)
                         }
                     }
                 }

                MyControls.Button {
                    text: qsTr("Set Timezone")
                    onClicked: {
                        dialogSetTz.open()
                    }
                }

                Label {
                    font.family: bold.font.family
                    font.pixelSize: 16
                    text: qsTr("DateTime")
                }

                MyControls.TextField {
                    id: textFieldDateTime
                    implicitWidth: 300
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    placeholderText: "YYYY-MM-DD HH:MM:SS"
                    text: new Date().toLocaleString(Qt.locale(), "yyyy-MM-dd hh:mm:ss")
                    inputMethodHints: Qt.ImhPreferNumbers
                    validator: RegularExpressionValidator {
                        regularExpression: /^(19|20)\d\d-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01]) (0[0-9]|1[0-9]|2[0-3]):([0-5][0-9]):([0-5][0-9])$/
                    }
                }

                Dialog {
                     id: dialogSetDateTime
                     modal: true
                     standardButtons: Dialog.Ok | Dialog.Cancel
                     title: qsTr("Please input user password")

                     contentItem: Rectangle {
                         color: "#FFFFFF"
                         implicitHeight: 50
                         implicitWidth: 200

                         TextField {
                             id: textFieldPswSetDateTime
                             anchors.centerIn: parent
                             echoMode: TextInput.Password
                             placeholderText: qsTr("Input user password")
                             focus: true
                         }
                     }

                     onAccepted: {
                         if (textFieldPswSetDateTime.text) {
                             timeEditor.set_time(textFieldDateTime.text, textFieldPswSetDateTime.text)
                         }
                     }
                 }

                MyControls.Button {
                    text: qsTr("Set DateTime")
                    onClicked: {
                        dialogSetDateTime.open()
                    }
                }

                Label {
                    font.family: bold.font.family
                    font.pixelSize: 16
                    text: qsTr("NTP Servers")
                }

                MyControls.TextField {
                    id: textFieldNTP
                    implicitWidth: 300
                    placeholderText: qsTr("Servers are separated by space")
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    inputMethodHints: Qt.ImhPreferNumbers
                }

                Dialog {
                     id: dialogSetNTP
                     modal: true
                     standardButtons: Dialog.Ok | Dialog.Cancel
                     title: qsTr("Please input user password")

                     contentItem: Rectangle {
                         color: "#FFFFFF"
                         implicitHeight: 50
                         implicitWidth: 200

                         TextField {
                             id: textFieldPswSetNTP
                             anchors.centerIn: parent
                             echoMode: TextInput.Password
                             placeholderText: qsTr("Input user password")
                             focus: true
                         }
                     }

                     onAccepted: {
                         if (textFieldPswSetNTP.text) {
                             timeEditor.add_ntp_servers(textFieldNTP.text, textFieldPswSetNTP.text)
                         }
                     }
                 }

                MyControls.Button {
                    text: qsTr("Set NTP Servers")
                    onClicked: {
                        dialogSetNTP.open()
                    }
                }
            }
        }
    }
}
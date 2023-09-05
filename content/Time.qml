import QtQuick 6.5
import QtQuick.Controls 6.5
import QtQuick.Layouts 6.5

import Controls as MyControls

import src.time


Item {
    MyControls.VertTabBar {
        id: vertTabBarTime
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.top: parent.top
        width: 180

        MyControls.TabButton {
            anchors.left: parent.left
            anchors.right: parent.right
            text: qsTr("Time/Timezone")
        }

        MyControls.TabButton {
            anchors.left: parent.left
            anchors.right: parent.right
            text: qsTr("NTP Server")
        }
    }

    StackLayout {
        anchors.left: parent.left
        anchors.leftMargin: 196
        anchors.right: parent.right
        anchors.rightMargin: 16
        anchors.top: parent.top
        anchors.topMargin: 16
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 16
        currentIndex: vertTabBarTime.currentIndex

        TimeEditor {
            id: timeEditor
            // Component.onCompleted: timeEditor.Stdout.connect()
        }

        MyControls.GroupBox {
            Layout.fillHeight: true
            Layout.fillWidth: true
            height: 110

            Label {
                font.bold: true
                font.pixelSize: 16
                text: qsTr("Settings")
            }

            ColumnLayout {
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.verticalCenter: parent.verticalCenter
                spacing: 20

                RowLayout {
                    Label {
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
                         focus: true
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
                }

                RowLayout {
                    Label {
                        font.pixelSize: 16
                        text: qsTr("DateTime")
                    }

                    MyControls.TextField {
                        id: textFieldDateTime
                        implicitWidth: 300
                        placeholderText: "YYYY-MM-DD HH:MM:SS"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }

                    Dialog {
                         id: dialogSetDateTime
                         modal: true
                         focus: true
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
                }
            }
        }
    }
}
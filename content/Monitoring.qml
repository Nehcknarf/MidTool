import QtQuick 6.5
import QtQuick.Controls 6.5
import QtQuick.Layouts 6.5
import QtQuick.Dialogs 6.5

import Controls as MyControls

import src.process
import src.monitoring


Item {
    MyControls.GroupBox {
        id: groupBox

        anchors.left: parent.left
        anchors.leftMargin: 16
        anchors.top: parent.top
        anchors.topMargin: 16
        height: 160
        width: 400

        Label {
            font.bold: true
            font.pixelSize: 16
            text: qsTr("Middleware Service Management")
        }
        Process {
            id: process

            Component.onCompleted: process.Stdout.connect(textArea.append)
        }
        FileDialog {
            id: fileDialog

            currentFolder: "/nubomed"
            nameFilters: [qsTr("Json file (*.json)"), qsTr("Config file (*.conf)")]
            title: qsTr("Please select middleware config file")

            onAccepted: process.start_middleware(selectedFile)
        }
        RowLayout {
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.verticalCenter: parent.verticalCenter

            // Dialog {
            //     id: dialogPromote
            //
            //     modal: true
            //     standardButtons: Dialog.Ok | Dialog.Cancel
            //     title: "Please input user password."
            //
            //     contentItem: Rectangle {
            //         color: "#FFFFFF"
            //         implicitHeight: 50
            //         implicitWidth: 200
            //
            //         TextField {
            //             id: textFieldPsw
            //
            //             anchors.centerIn: parent
            //             echoMode: TextInput.Password
            //             placeholderText: qsTr("Input user password")
            //         }
            //     }
            //
            //     onAccepted: {
            //         if (textFieldPsw.text) {
            //             process.start_middleware(selectedFile)
            //         }
            //     }
            // }

            MyControls.Button {
                id: buttonStart

                text: qsTr("Start")

                onClicked: fileDialog.open()
            }
            MyControls.Button {
                id: buttonRestart

                text: qsTr("Restart")

                onClicked: process.restart_middleware()
            }
            MyControls.Button {
                id: buttonStop

                text: qsTr("Stop")

                onClicked: {
                    process.stop_middleware();
                    // process.kill()
                }
            }
        }
    }
    MyControls.GroupBox {
        id: groupBox1

        anchors.left: groupBox.right
        anchors.leftMargin: 16
        anchors.right: parent.right
        anchors.rightMargin: 16
        anchors.top: parent.top
        anchors.topMargin: 16
        height: 160

        Label {
            font.bold: true
            font.pixelSize: 16
            text: qsTr("Service Running Status")
        }
        Timer {
            interval: 1000
            repeat: true
            running: true

            onTriggered: listView.model.set_data()
        }
        ListView {
            id: listView

            anchors.bottomMargin: 50
            anchors.fill: parent
            anchors.leftMargin: 50
            anchors.rightMargin: 50
            anchors.topMargin: 50
            orientation: ListView.Horizontal

            delegate: Item {
                height: 40
                width: 100
                x: 5

                Column {
                    spacing: 10

                    Row {
                        spacing: 2

                        Text {
                            font.bold: true
                            text: name
                        }
                        Text {
                            text: percent + "%"
                        }
                    }
                    MyControls.ProgressBar {
                        value: percent / 100
                        width: 90
                    }
                }
            }
            model: SystemInfoModel {
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
        anchors.top: parent.top
        anchors.topMargin: 192

        Label {
            font.bold: true
            font.pixelSize: 16
            text: qsTr("Terminal Output")
        }
        MyControls.Button {
            anchors.right: parent.right
            anchors.top: parent.top
            text: qsTr("Clear")

            onClicked: textArea.clear()
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
                id: textArea

                anchors.fill: parent
                readOnly: true
            }
        }
    }
}
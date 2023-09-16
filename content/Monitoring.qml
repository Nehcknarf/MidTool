import QtQuick 6.5
import QtQuick.Controls 6.5
import QtQuick.Layouts 6.5
import QtQuick.Dialogs 6.5

import Controls as MyControls

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
            font.family: bold.font.family
            font.pixelSize: 16
            text: qsTr("Middleware Service Management")
        }

        MiddlewareManager {
            id: middlewareManager
            Component.onCompleted: middlewareManager.Stdout.connect(textArea.append)
        }
        // Dialog 临时方案
        Dialog {
            id: dialogStart
            modal: true
            standardButtons: Dialog.Ok | Dialog.Cancel
            title: qsTr("Please input user password")

            contentItem: Rectangle {
                color: "#FFFFFF"
                implicitHeight: 50
                implicitWidth: 200

                TextField {
                    id: textFieldPsw
                    anchors.centerIn: parent
                    echoMode: TextInput.Password
                    placeholderText: qsTr("Input user password")
                    focus: true
                    Keys.onReturnPressed: dialogStart.accept()
                }
            }

            onAccepted: {
                if (textFieldPsw.text) {
                    fileDialog.open()
                }
            }
        }

        Dialog {
            id: dialogRestart
            modal: true
            standardButtons: Dialog.Ok | Dialog.Cancel
            title: qsTr("Please input user password")

            contentItem: Rectangle {
                color: "#FFFFFF"
                implicitHeight: 50
                implicitWidth: 200

                TextField {
                    id: textFieldPsw1
                    anchors.centerIn: parent
                    echoMode: TextInput.Password
                    placeholderText: qsTr("Input user password")
                    focus: true
                    Keys.onReturnPressed: dialogRestart.accept()
                }
            }

            onAccepted: {
                if (textFieldPsw1.text) {
                    middlewareManager.restart_middleware(textFieldPsw1.text)
                }
            }
        }

        Dialog {
            id: dialogStop
            modal: true
            standardButtons: Dialog.Ok | Dialog.Cancel
            title: qsTr("Please input user password")

            contentItem: Rectangle {
                color: "#FFFFFF"
                implicitHeight: 50
                implicitWidth: 200

                TextField {
                    id: textFieldPsw2
                    anchors.centerIn: parent
                    echoMode: TextInput.Password
                    placeholderText: qsTr("Input user password")
                    focus: true
                    Keys.onReturnPressed: dialogStop.accept()
                }
            }

            onAccepted: {
                if (textFieldPsw2.text) {
                    middlewareManager.stop_middleware(textFieldPsw2.text)
                }
            }
        }

        FileDialog {
            id: fileDialog

            currentFolder: "/nubomed"
            nameFilters: [qsTr("Json file (*.json)")]
            title: qsTr("Please select middleware config file, if no need just cancel")

            onAccepted: middlewareManager.start_middleware_pm2(selectedFile)
            onRejected: middlewareManager.start_middleware_sv(textFieldPsw.text)
        }

        RowLayout {
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.verticalCenter: parent.verticalCenter

            MyControls.Button {
                id: buttonStart
                text: qsTr("Start")
                onClicked: {
                    dialogStart.open()
                }
            }
            MyControls.Button {
                id: buttonRestart
                text: qsTr("Restart")
                onClicked: {
                    dialogRestart.open()
                }
            }
            MyControls.Button {
                id: buttonStop
                text: qsTr("Stop")
                onClicked: {
                    dialogStop.open()
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
            font.family: bold.font.family
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
                width: 110
                x: 5

                Column {
                    spacing: 10

                    Row {
                        spacing: 2

                        Text {
                            font.family: medium.font.family
                            font.pixelSize: 16
                            text: name
                        }
                        Text {
                            font.family: medium.font.family
                            font.pixelSize: 16
                            text: percent + "%"
                        }
                    }
                    MyControls.ProgressBar {
                        value: percent / 100
                        width: 90
                    }
                }
            }
            model: SystemInfoModel {}
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
            font.family: bold.font.family
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
                font.family: medium.font.family
                font.pixelSize: 16
                readOnly: true
            }
        }
    }
}
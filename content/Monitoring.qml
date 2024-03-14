import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs

import Controls as MyControls
import Components as MyComponents

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
            font.family: bold.name
            font.pixelSize: 16
            text: qsTr("Middleware Service Management")
        }

        MiddlewareManager {
            id: middlewareManager
            Component.onCompleted: middlewareManager.Stdout.connect(terminalOutput.textArea.append)
        }

        MyComponents.Dialog {
            id: dialogStart
            onAction: {
                middlewareManager.start_middleware(input)
            }
        }

        MyComponents.Dialog {
            id: dialogRestart
            onAction: {
                middlewareManager.restart_middleware(input)
            }
        }

        MyComponents.Dialog {
            id: dialogStop
            onAction: {
                middlewareManager.stop_middleware(input)
            }
        }

        // FileDialog {
        //     id: fileDialog
        //     currentFolder: "/nubomed"
        //     nameFilters: [qsTr("Json file (*.json)")]
        //     title: qsTr("Please select middleware config file, if no need just cancel")
        //     onAccepted: middlewareManager.start_middleware(dialogStart.input)
        // }

        RowLayout {
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.verticalCenter: parent.verticalCenter

            MyControls.Button {
                id: buttonStart
                text: qsTr("Start")
                onClicked: {
                    if (productType === 1) {
                        dialogStart.open()
                    } else {
                        middlewareManager.start_middleware("")
                    }
                }
            }

            MyControls.Button {
                id: buttonRestart
                text: qsTr("Restart")
                onClicked: {
                    if (productType === 1) {
                        dialogRestart.open()
                    } else {
                        middlewareManager.restart_middleware("")
                    }
                }
            }

            MyControls.Button {
                id: buttonStop
                text: qsTr("Stop")
                onClicked: {
                    if (productType === 1) {
                        dialogStop.open()
                    } else {
                        middlewareManager.stop_middleware("")
                    }
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
            font.family: bold.name
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
            anchors.fill: parent
            anchors.leftMargin: 50
            anchors.rightMargin: 50
            anchors.topMargin: 40
            anchors.bottomMargin: 40
            orientation: ListView.Horizontal

            delegate: Item {
                width: 85

                Column {
                    Text {
                        font.family: medium.name
                        font.pixelSize: 16
                        text: name
                    }

                    Text {
                        font.family: medium.name
                        font.pixelSize: 16
                        text: status.includes(".") ? status + "%" : status
                    }

                    MyControls.ProgressBar {
                        value: status / 100
                        width: 75
                        visible: status.includes(".")
                    }
                }
            }
            model: SystemInfoModel {}
        }
    }

    MyComponents.TerminalOutput {
        id: terminalOutput
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 16
        anchors.left: parent.left
        anchors.leftMargin: 16
        anchors.right: parent.right
        anchors.rightMargin: 16
        anchors.top: parent.top
        anchors.topMargin: 192
    }
}
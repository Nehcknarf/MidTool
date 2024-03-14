import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs

import Controls as MyControls
import Components as MyComponents

import src.reader


Item {
    Reader {
        id: reader
        Component.onCompleted: reader.Stdout.connect(terminalOutputRd.textArea.append)
    }

    MyControls.GroupBox {
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
            text: qsTr("Terminal Input")
        }

        RowLayout {
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.verticalCenter: parent.verticalCenter

            MyControls.Button {
                text: qsTr("Start configuration")
                onClicked: reader.start_config()
            }

            MyControls.Button {
                text: qsTr("Quit")
                onClicked: reader.write("q")
            }

            ToolSeparator {
                rightPadding: 3
                leftPadding: 3
                bottomPadding: 0
                topPadding: 0
                Layout.fillHeight: true
            }

            MyControls.TextField {
                id: textFieldKeyData
                implicitWidth: 300
                Keys.onReturnPressed: btnSend.clicked()
            }

            MyControls.Button {
                id: btnSend
                text: qsTr("Send")
                onClicked: {
                    reader.write(textFieldKeyData.text)
                    textFieldKeyData.clear()
                }
            }

            ToolSeparator {
                rightPadding: 3
                leftPadding: 3
                bottomPadding: 0
                topPadding: 0
                Layout.fillHeight: true
            }

            FolderDialog {
                id: folderDialogRd
                title: qsTr("Please select a folder to save records")
                currentFolder: "/media"
                acceptLabel: qsTr("Save")
                onAccepted: {
                    reader.record(selectedFolder, terminalOutputRd.textArea.text)
                }
            }

            MyControls.Button {
                text: qsTr("Save to...")
                onClicked: folderDialogRd.open()
            }
        }
    }

    MyComponents.TerminalOutput {
        id: terminalOutputRd
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 16
        anchors.left: parent.left
        anchors.leftMargin: 16
        anchors.right: parent.right
        anchors.rightMargin: 16
        anchors.top: parent.top
        anchors.topMargin: 142
    }
}
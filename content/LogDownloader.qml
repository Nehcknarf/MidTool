import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs

import Controls as MyControls
import Components as MyComponents

import src.logDownloader


Item {
    property int logType: 1

    LogDownloader {
        id: logDownloader
        Component.onCompleted: logDownloader.Output.connect(terminalOutputLog.textArea.append)
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
            text: qsTr("Settings")
        }

        RowLayout {
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.verticalCenter: parent.verticalCenter

            ButtonGroup {
                id: buttonGroup
                exclusive: true
            }

            MyControls.RadioButton {
                text: qsTr("Middleware logs")
                ButtonGroup.group: buttonGroup
                onClicked: logType = 1
            }

            MyControls.RadioButton {
                text: qsTr("System logs")
                ButtonGroup.group: buttonGroup
                onClicked: logType = 2
            }

            ToolSeparator {
                rightPadding: 3
                leftPadding: 3
                bottomPadding: 0
                topPadding: 0
                Layout.fillHeight: true
            }

            Label {
                font.family: bold.name
                font.pixelSize: 16
                text: qsTr("Start Date")
            }

            MyControls.TextField {
                id: textFieldStratTime
                placeholderText: "YYYY-MM-DD"
                text: new Date().toLocaleDateString(Qt.locale(), "yyyy-MM-dd")
                inputMethodHints: Qt.ImhDate | Qt.ImhFormattedNumbersOnly
                validator: RegularExpressionValidator {
                    regularExpression: /^(19|20)\d\d-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$/
                }
            }

            Label {
                font.family: bold.name
                font.pixelSize: 16
                text: qsTr("End Date")
            }

            MyControls.TextField {
                id: textFieldEndTime
                placeholderText: "YYYY-MM-DD"
                text: new Date().toLocaleDateString(Qt.locale(), "yyyy-MM-dd")
                inputMethodHints: Qt.ImhDate | Qt.ImhFormattedNumbersOnly
                validator: RegularExpressionValidator {
                    regularExpression: /^(19|20)\d\d-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$/
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
                id: folderDialog
                title: qsTr("Please select a folder to save logs")
                currentFolder: "/media"
                acceptLabel: qsTr("Save")
                onAccepted: {
                    logDownloader.download(selectedFolder, textFieldStratTime.text, textFieldEndTime.text, logType)
                }
            }

            MyControls.Button {
                text: qsTr("Save to...")
                onClicked: folderDialog.open()
            }
        }
    }

    MyComponents.TerminalOutput {
        id: terminalOutputLog
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
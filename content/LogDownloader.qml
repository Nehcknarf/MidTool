import QtQuick 6.5
import QtQuick.Controls 6.5
import QtQuick.Layouts 6.5
import QtQuick.Dialogs 6.5

import Controls as MyControls

import src.logDownloader


Item {
    property int logType: 1

    LogDownloader {
        id: logDownloader
        Component.onCompleted: logDownloader.Output.connect(textAreaDownload.append)
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
            font.family: bold.font.family
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
                font.family: bold.font.family
                font.pixelSize: 16
                text: qsTr("Start Date")
            }

            MyControls.TextField {
                id: textFieldStratTime
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                placeholderText: "YYYY-MM-DD"
                text: new Date().toLocaleDateString(Qt.locale(), "yyyy-MM-dd")
                inputMethodHints: Qt.ImhDate | Qt.ImhFormattedNumbersOnly
                validator: RegularExpressionValidator {
                    regularExpression: /^(19|20)\d\d-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$/
                }
            }

            Label {
                font.family: bold.font.family
                font.pixelSize: 16
                text: qsTr("End Date")
            }

            MyControls.TextField {
                id: textFieldEndTime
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
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

    MyControls.GroupBox {
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 16
        anchors.left: parent.left
        anchors.leftMargin: 16
        anchors.right: parent.right
        anchors.rightMargin: 16
        anchors.top: parent.top
        anchors.topMargin: 142

        Label {
            font.family: bold.font.family
            font.pixelSize: 16
            text: qsTr("Terminal Output")
        }

        MyControls.Button {
            anchors.right: parent.right
            anchors.top: parent.top
            text: qsTr("Clear")
            onClicked: textAreaDownload.clear()
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
                id: textAreaDownload
                anchors.fill: parent
                font.family: medium.font.family
                font.pixelSize: 16
                readOnly: true
            }
        }
    }
}
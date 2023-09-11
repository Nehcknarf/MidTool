import QtQuick 6.5
import QtQuick.Controls 6.5
import QtQuick.Layouts 6.5

import Controls as MyControls


Item {
    property var locale: Qt.locale()
    property date currentDate: new Date()
    property string dateString

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
                id: childGroup
                exclusive: true
            }

            MyControls.CheckBox {
                id: checkBoxSys
                text: qsTr("System logs")
                ButtonGroup.group: childGroup
            }

            MyControls.CheckBox {
                id: checkBoxMid
                text: qsTr("Middleware logs")
                ButtonGroup.group: childGroup
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
                implicitWidth: 150
                placeholderText: "YYYY-MM-DD"
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter

                Component.onCompleted: {
                    dateString = currentDate.toLocaleDateString();
                    print(Date.fromLocaleDateString(dateString));
                }
            }

            Label {
                font.family: bold.font.family
                font.pixelSize: 16
                text: qsTr("End Date")
            }

            MyControls.TextField {
                id: textFieldEndTime
                implicitWidth: 150
                placeholderText: "YYYY-MM-DD"
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
            }

            ToolSeparator {
                rightPadding: 3
                leftPadding: 3
                bottomPadding: 0
                topPadding: 0

                Layout.fillHeight: true
            }

            MyControls.Button {
                text: qsTr("Save to...")
                // onClicked: {
                // }
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
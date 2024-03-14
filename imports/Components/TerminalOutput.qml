import QtQuick
import QtQuick.Controls

import Controls as MyControls


MyControls.GroupBox {
    property alias textArea: textArea

    Label {
        font.family: bold.name
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
        anchors.topMargin: 50

        ScrollBar.vertical.position: 1.0 - ScrollBar.vertical.size
        ScrollBar.horizontal.position: 0.0

        TextArea {
            id: textArea
            anchors.fill: parent
            font.family: medium.name
            font.pixelSize: 16
            readOnly: true

            background: Rectangle {
                border.color: "#CAD0E0"
                radius: 8
            }
        }
    }
}
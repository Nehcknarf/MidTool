import QtQuick
import QtQuick.Controls

import Controls as MyControls


MyControls.GroupBox {
    property alias textArea: textArea

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
        anchors.topMargin: 50

        ScrollBar.horizontal.interactive: true
        ScrollBar.vertical.interactive: true

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
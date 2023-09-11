import QtQuick
import QtQuick.Controls

CheckBox {
    id: control
    text: qsTr("CheckBox")
    checked: true

    indicator: Rectangle {
        implicitWidth: 32
        implicitHeight: 32
        x: control.leftPadding
        y: parent.height / 2 - height / 2
        radius: 8
        color: "#cad0e0"

        Rectangle {
            width: 26
            height: 26
            x: parent.height / 2 - height / 2
            y: parent.height / 2 - height / 2
            radius: 8
            color: "#00a572"
            visible: control.checked
        }
    }

    contentItem: Text {
        text: control.text
        font.family: medium.font.family
        font.pixelSize: 16
        opacity: 0.5
        color: "#181D41"
        verticalAlignment: Text.AlignVCenter
        leftPadding: control.indicator.width + control.spacing
    }
}
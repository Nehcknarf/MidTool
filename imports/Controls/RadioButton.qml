import QtQuick
import QtQuick.Controls

RadioButton {
    id: control
    text: qsTr("RadioButton")
    checked: true

    indicator: Rectangle {
        implicitWidth: 32
        implicitHeight: 32
        x: control.leftPadding
        y: parent.height / 2 - height / 2
        radius: 16
        color: "#cad0e0"

        Rectangle {
            width: 22
            height: 22
            x: parent.height / 2 - height / 2
            y: parent.height / 2 - height / 2
            radius: 11
            color: "#00a572"
            visible: control.checked
        }
    }

    contentItem: Text {
        text: control.text
        font.family: medium.name
        font.pixelSize: 16
        opacity: 0.5
        color: "#181D41"
        verticalAlignment: Text.AlignVCenter
        leftPadding: control.indicator.width + control.spacing
    }
}
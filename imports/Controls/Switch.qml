import QtQuick
import QtQuick.Controls

Switch {
    id: control
    font.pixelSize: 16

    indicator: Rectangle {
        implicitWidth: 64
        implicitHeight: 32
        x: control.leftPadding
        y: parent.height / 2 - height / 2
        radius: 16
        color: control.checked ? "#00a572" : "#cad0e0"

        Rectangle {
            x: control.checked ? parent.width - width - 3 : 3
            y: parent.height / 2 - height / 2
            width: 26
            height: 26
            radius: 13
            color: "#ffffff"
        }
    }

    contentItem: Text {
        text: control.text
        font: control.font
        opacity: 0.5
        color: "#181D41"
        verticalAlignment: Text.AlignVCenter
        leftPadding: control.indicator.width + control.spacing
        // rightPadding: control.indicator.width + control.spacing
    }
}
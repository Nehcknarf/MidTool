import QtQuick
import QtQuick.Controls

Button {
    id: control
    font.pixelSize: 16

    contentItem: Text {
        text: control.text
        font: control.font
        color: "#FFFFFF"
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        elide: Text.ElideRight
    }

    background: Rectangle {
        implicitWidth: 100
        implicitHeight: 40
        color: control.down ? "#3385E6" : "#0066E0"
        radius: 8
    }
}
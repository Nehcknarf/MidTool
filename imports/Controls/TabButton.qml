import QtQuick
import QtQuick.Controls

TabButton {
    id: control

    contentItem: Text {
        text: control.text
        font.family: bold.name
        font.pixelSize: 16
        color: control.checked ? "#FFFFFF" : "#181D41"
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        elide: Text.ElideRight
    }

    background: Rectangle {
        implicitWidth: 120
        implicitHeight: 60
        color: control.checked ? "#0066E0" : "#FFFFFF"
    }
}
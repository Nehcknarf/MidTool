import QtQuick
import QtQuick.Controls

TextField {
    id: control
    placeholderText: qsTr("Enter")
    font.family: medium.font.family
    font.pixelSize: 16

    background: Rectangle {
        implicitWidth: 100
        implicitHeight: 40
        color: "#FFFFFF"
        border.color: "#CAD0E0"
        radius: 8
    }
}
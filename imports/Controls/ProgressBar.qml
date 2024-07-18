import QtQuick
import QtQuick.Controls

ProgressBar {
    id: control
    value: 0.5
    padding: 2

    background: Rectangle {
        implicitWidth: 52
        implicitHeight: 14
        color: "#e6e6e6"
        radius: 8
    }

    contentItem: Item {
        implicitWidth: 50
        implicitHeight: 12

        Rectangle {
            width: control.visualPosition * parent.width
            height: parent.height
            radius: 12
            color: "#00a572"
        }
    }
}
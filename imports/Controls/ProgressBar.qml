import QtQuick
import QtQuick.Controls

ProgressBar {
    id: control
    value: 0.5
    padding: 2

    background: Rectangle {
        implicitWidth: 50
        implicitHeight: 10
        color: "#e6e6e6"
        radius: 8
    }

    contentItem: Item {
        implicitWidth: 50
        implicitHeight: 8

        Rectangle {
            width: control.visualPosition * parent.width
            height: parent.height
            radius: 8
            color: "#00a572"
        }
    }
}
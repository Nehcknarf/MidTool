import QtQuick
import QtQuick.Controls

GroupBox {
    id: control

    background: Rectangle {
        y: control.topPadding - control.bottomPadding
        width: parent.width
        height: parent.height - control.topPadding + control.bottomPadding
        color: "#FFFFFF"
        radius: 8
    }

    label: Label {
        x: control.leftPadding
        width: control.availableWidth
        text: control.title
        color: "#181D41"
        elide: Text.ElideRight
    }
}
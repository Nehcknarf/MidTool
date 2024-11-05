import QtQuick
import QtQuick.Controls.Basic

ComboBox {
    id: control

    delegate: ItemDelegate {
        id: delegate

        required property var model
        required property int index

        width: control.width
        contentItem: Text {
            text: delegate.model[control.textRole]
            color: "#181D41"
            font.family: medium.name
            font.pixelSize: 16
            elide: Text.ElideRight
            verticalAlignment: Text.AlignVCenter
        }
        highlighted: control.highlightedIndex === index
    }

    indicator: Canvas {
        id: canvas
        x: control.width - width - 10
        y: control.topPadding + (control.availableHeight - height) / 2
        width: 24
        height: 16
        contextType: "2d"

        Connections {
            target: control
            function onPressedChanged() { canvas.requestPaint(); }
        }

        onPaint: {
            context.reset();
            context.moveTo(0, 0);
            context.lineTo(width, 0);
            context.lineTo(width / 2, height);
            context.closePath();
            context.fillStyle = "#8B8EA0";
            context.fill();
        }
    }

    contentItem: Text {
        leftPadding: 13
        rightPadding: control.indicator.width + control.spacing

        text: control.displayText
        font.family: medium.name
        font.pixelSize: 16
        color: "#181D41"
        verticalAlignment: Text.AlignVCenter
        elide: Text.ElideRight
    }

    background: Rectangle {
        implicitWidth: 120
        implicitHeight: 40
        border.color: "#CAD0E0"
        border.width: control.visualFocus ? 2 : 1
        radius: 8
    }

    popup: Popup {
        y: control.height - 1
        width: control.width
        implicitHeight: contentItem.implicitHeight
        popupType: Popup.Window
        padding: 1

        contentItem: ListView {
            clip: true
            implicitHeight: contentHeight
            model: control.popup.visible ? control.delegateModel : null
            currentIndex: control.highlightedIndex

            ScrollIndicator.vertical: ScrollIndicator { }
        }

        background: Rectangle {
            border.color: "#CAD0E0"
            radius: 8
        }
    }
}
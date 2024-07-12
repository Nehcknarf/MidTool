import QtQuick
import QtQuick.Controls

import Controls as MyControls


Dialog {
    id: dialog
    x: (parent.width - width) / 2
    y: parent.height / 2 - height
    modal: true

    // 导出属性
    property alias placeholder: textField.placeholderText
    property alias echoMode: textField.echoMode
    property alias inputMethodHints: textField.inputMethodHints
    property alias input: textField.text
    // 导出信号
    signal action

    // Overlay.modal: Rectangle {
    //     color: "transparent"
    // }

    background: Rectangle {
        border.color: "#CAD0E0"
        radius: 8
    }

    header: Text {
        lineHeight: 2
        text: qsTr("Please input user password")
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        font.family: medium.name
        font.pixelSize: 16
    }

    contentItem: MyControls.TextField {
        id: textField
        placeholderText: qsTr("Input user password")
        echoMode: TextInput.Password
        focus: true
        // Keys.onReturnPressed: dialog.accept()
    }

    footer: DialogButtonBox {
        MyControls.Button {
            width: 100
            height: 40
            text: qsTr("Ok")
            DialogButtonBox.buttonRole: DialogButtonBox.AcceptRole
        }
        Button {
            width: 100
            height: 40
            id: buttonCancel
            text: qsTr("Cancel")
            DialogButtonBox.buttonRole: DialogButtonBox.RejectRole

            contentItem: Text {
                text: buttonCancel.text
                font.family: medium.name
                font.pixelSize: 16
                color: "#0066E0"
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                elide: Text.ElideRight
            }

            background: Rectangle {
                color: buttonCancel.down ? "#878686" : "#FFFFFF"
                border.color: "#CAD0E0"
                radius: 8
            }
        }
        onAccepted: action()
    }
}
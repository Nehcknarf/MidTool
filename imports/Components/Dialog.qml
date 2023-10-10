import QtQuick
import QtQuick.Controls


Dialog {
    id: dialog

    // 导出属性
    property alias placeholder: textField.placeholderText
    property alias echoMode: textField.echoMode
    property alias inputMethodHints: textField.inputMethodHints
    property alias input: textField.text
    // 导出信号
    signal action

    title: qsTr("Please input user password")
    standardButtons: Dialog.Ok | Dialog.Cancel
    modal: true

    Overlay.modal: Rectangle {
        color: "transparent"
    }

    contentItem: Rectangle {
        color: "#FFFFFF"
        implicitHeight: 50
        implicitWidth: 200

        TextField {
            id: textField
            anchors.centerIn: parent
            placeholderText: qsTr("Input user password")
            echoMode: TextInput.Password
            focus: true
            Keys.onReturnPressed: dialog.accept()
        }
    }

    onAccepted: {
        if (textField.text) {
            dialog.action()
        }
    }
}
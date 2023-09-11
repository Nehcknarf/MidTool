import QtQuick 6.5
import QtQuick.VirtualKeyboard 6.5


Window {
    title: "MidTool"
    // flags: Qt.FramelessWindowHint | Qt.Window | Qt.WindowStaysOnTopHint
    x: Screen.width / 2 - width / 2
    y: Screen.height / 2 - height / 2
    width: mainScreen.width
    height: mainScreen.height
    visible: true

    FontLoader {
        id: bold
        source: "qrc:/content/fonts/OPlusSans3-Bold.ttf"
    }
    FontLoader {
        id: medium
        source: "qrc:/content/fonts/OPlusSans3-Medium.ttf"
    }

    MainScreen {
        id: mainScreen
    }

    InputPanel {
        id: inputPanel

        property bool showKeyboard: active

        anchors.left: parent.left
        anchors.leftMargin: 1280 / 5
        anchors.right: parent.right
        anchors.rightMargin: 1280 / 5
        y: showKeyboard ? parent.height - height : parent.height

        Behavior on y  {
            NumberAnimation {
                duration: 200
                easing.type: Easing.InOutQuad
            }
        }
    }
}


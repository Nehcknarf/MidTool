import QtQuick
import QtQuick.VirtualKeyboard
import QtQuick.VirtualKeyboard.Settings


Window {
    id: window
    title: "MidTool"
    x: Screen.width / 2 - width / 2
    y: Screen.height / 2 - height / 2
    width: mainScreen.width
    height: mainScreen.height
    visible: true
    flags: argCurrentIndex ? Qt.FramelessWindowHint | Qt.Window | Qt.WindowStaysOnTopHint : Qt.FramelessWindowHint | Qt.Window

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
        property bool showKeyboard: active

        y: showKeyboard ? parent.height - height : parent.height
        anchors.left: parent.left
        anchors.leftMargin: mainScreen.width / 5
        anchors.right: parent.right
        anchors.rightMargin: mainScreen.width / 5

        Component.onCompleted: VirtualKeyboardSettings.activeLocales  = "en_US"
    }
}

import QtQuick 6.5
import QtQuick.VirtualKeyboard 6.5


Window {
    height: mainScreen.height
    title: "MidTool"
    visible: true
    // flags: Qt.FramelessWindowHint | Qt.Window | Qt.WindowStaysOnTopHint
    width: mainScreen.width

    FontLoader {
        id: fontLoader
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


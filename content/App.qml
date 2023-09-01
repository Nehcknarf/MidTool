// Copyright (C) 2021 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only

import QtQuick 6.5
import MidToolUI
import QtQuick.VirtualKeyboard 6.5

Window {
    height: mainScreen.height
    title: "MidTool"
    visible: true
    // flags: Qt.FramelessWindowHint | Qt.Window | Qt.WindowStaysOnTopHint
    width: mainScreen.width

    MainScreen {
        id: mainScreen

    }
    InputPanel {
        id: inputPanel

        property bool showKeyboard: active

        anchors.left: parent.left
        anchors.leftMargin: Constants.width / 5
        anchors.right: parent.right
        anchors.rightMargin: Constants.width / 5
        y: showKeyboard ? parent.height - height : parent.height

        Behavior on y  {
            NumberAnimation {
                duration: 200
                easing.type: Easing.InOutQuad
            }
        }
    }
}


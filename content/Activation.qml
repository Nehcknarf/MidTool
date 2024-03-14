import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import Controls as MyControls
import Components as MyComponents

import src.activation


Item {
    Activation {
        id: activation
        Component.onCompleted: activation.Stdout.connect(terminalOutputAs.textArea.append)
    }

    MyControls.GroupBox {
        anchors.left: parent.left
        anchors.leftMargin: 16
        anchors.right: parent.right
        anchors.rightMargin: 16
        anchors.top: parent.top
        anchors.topMargin: 16
        height: 110

        Label {
            font.family: bold.name
            font.pixelSize: 16
            text: qsTr("Online Activation")
        }

        RowLayout {
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.verticalCenter: parent.verticalCenter

            Label {
                font.family: bold.name
                font.pixelSize: 16
                text: qsTr("Key")
            }

            MyControls.TextField {
                id: textFieldKeyPart1
                // maximumLength: 4
                validator: RegularExpressionValidator {
                    regularExpression: /[0-9a-zA-Z]{1,4}/
                }
                onAccepted: textFieldKeyPart2.focus = true
            }

            Label {
                font.family: bold.name
                font.pixelSize: 16
                text: qsTr("-")
            }

            MyControls.TextField {
                id: textFieldKeyPart2
                validator: RegularExpressionValidator {
                    regularExpression: /[0-9a-zA-Z]{1,4}/
                }
                onAccepted: textFieldKeyPart3.focus = true
            }

            Label {
                font.family: bold.name
                font.pixelSize: 16
                text: qsTr("-")
            }

            MyControls.TextField {
                id: textFieldKeyPart3
                validator: RegularExpressionValidator {
                    regularExpression: /[0-9a-zA-Z]{1,4}/
                }
                onAccepted: textFieldKeyPart4.focus = true
            }

            Label {
                font.family: bold.name
                font.pixelSize: 16
                text: qsTr("-")
            }

            MyControls.TextField {
                id: textFieldKeyPart4
                validator: RegularExpressionValidator {
                    regularExpression: /[0-9a-zA-Z]{1,4}/
                }
            }

            MyControls.Button {
                text: qsTr("Activate")
                onClicked: {
                    activation.activate_arcsoft(textFieldKeyPart1.text, textFieldKeyPart2.text, textFieldKeyPart3.text, textFieldKeyPart4.text)
                }
            }
        }
    }

    MyComponents.TerminalOutput {
        id: terminalOutputAs
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 16
        anchors.left: parent.left
        anchors.leftMargin: 16
        anchors.right: parent.right
        anchors.rightMargin: 16
        anchors.top: parent.top
        anchors.topMargin: 142
    }
}
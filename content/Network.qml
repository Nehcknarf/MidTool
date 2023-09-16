import QtQuick 6.5
import QtQuick.Controls 6.5
import QtQuick.Layouts 6.5
import QtQuick.Dialogs 6.5

import Controls as MyControls

import src.network


Item {
    MyControls.VertTabBar {
        id: vertTabBarNetwork
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.top: parent.top
        width: 180

        MyControls.TabButton {
            anchors.left: parent.left
            anchors.right: parent.right
            text: qsTr("Diagnosis")
        }

        MyControls.TabButton {
            anchors.left: parent.left
            anchors.right: parent.right
            text: qsTr("Route")
        }
    }

    StackLayout {
        anchors.left: parent.left
        anchors.leftMargin: 196
        anchors.right: parent.right
        anchors.rightMargin: 16
        anchors.top: parent.top
        anchors.topMargin: 16
        anchors.bottom: groupBoxNetwork.top
        anchors.bottomMargin: 16
        currentIndex: vertTabBarNetwork.currentIndex

        Network {
            id: network
            Component.onCompleted: network.Stdout.connect(textAreaNetwork.append)
        }

         MyControls.GroupBox {
             Layout.fillWidth: true
             height: 110

             Label {
                 font.family: bold.font.family
                 font.pixelSize: 16
                 text: qsTr("Telnet")
             }

             RowLayout {
                 anchors.horizontalCenter: parent.horizontalCenter
                 anchors.verticalCenter: parent.verticalCenter

                 Label {
                    font.family: bold.font.family
                    font.pixelSize: 16
                    text: qsTr("IP address")
                }

                MyControls.TextField {
                     id: textFieldIp
                     implicitWidth: 150
                     // inputMask: "000.000.000.000;_"
                     inputMethodHints: Qt.ImhDigitsOnly
                }

                 Label {
                    font.family: bold.font.family
                    font.pixelSize: 16
                    text: qsTr("Port")
                }

                 MyControls.TextField {
                     id: textFieldPort
                     implicitWidth: 70
                     inputMethodHints: Qt.ImhDigitsOnly
                }

                MyControls.Button {
                    text: qsTr("Connect")
                    onClicked: {
                        network.telnet(textFieldIp.text, textFieldPort.text)
                    }
                }

                MyControls.Button {
                    text: qsTr("Kill telnet process")
                    onClicked: {
                        network.kill()
                    }
                }
             }
         }

         MyControls.GroupBox {
             Layout.fillWidth: true
             height: 110

             Label {
                 font.family: bold.font.family
                 font.pixelSize: 16
                 text: qsTr("Route")
             }

             ColumnLayout {
                 anchors.horizontalCenter: parent.horizontalCenter
                 anchors.verticalCenter: parent.verticalCenter
                 spacing: 20

                 RowLayout {
                     MyControls.Button {
                         text: qsTr("Show route table")
                         onClicked: {
                             network.show_route()
                         }
                     }
                 }

                 RowLayout {
                     Label {
                         font.family: bold.font.family
                         font.pixelSize: 16
                         text: qsTr("Destination")
                     }

                     MyControls.TextField {
                         id: textFieldDestination
                         implicitWidth: 150
                         // inputMask: "000.000.000.000;_"
                         inputMethodHints: Qt.ImhDigitsOnly
                     }

                     Label {
                         font.family: bold.font.family
                         font.pixelSize: 16
                         text: qsTr("Genmask")
                     }

                     MyControls.TextField {
                         id: textFieldGenmask
                         implicitWidth: 150
                         inputMethodHints: Qt.ImhDigitsOnly
                     }

                     Label {
                         font.family: bold.font.family
                         font.pixelSize: 16
                         text: qsTr("Gateway")
                     }

                     MyControls.TextField {
                         id: textFieldGateway
                         implicitWidth: 230
                         placeholderText: qsTr("Leave empty when deleting")
                         inputMethodHints: Qt.ImhDigitsOnly
                     }

                     Dialog {
                         id: dialogAddRoute
                         modal: true
                         standardButtons: Dialog.Ok | Dialog.Cancel
                         title: qsTr("Please input user password")

                         contentItem: Rectangle {
                             color: "#FFFFFF"
                             implicitHeight: 50
                             implicitWidth: 200

                             TextField {
                                 id: textFieldPswAddRoute
                                 anchors.centerIn: parent
                                 echoMode: TextInput.Password
                                 placeholderText: qsTr("Input user password")
                                 focus: true
                                 Keys.onReturnPressed: dialogAddRoute.accept()
                             }
                         }

                         onAccepted: {
                             if (textFieldPswAddRoute.text) {
                                 network.add_route(
                                     textFieldDestination.text,
                                     textFieldGenmask.text,
                                     textFieldGateway.text,
                                     textFieldPswAddRoute.text
                                 )
                             }
                         }
                     }

                     MyControls.Button {
                         text: qsTr("+")
                         implicitWidth: 40
                         onClicked: dialogAddRoute.open()
                     }

                     Dialog {
                         id: dialogDelRoute
                         modal: true
                         standardButtons: Dialog.Ok | Dialog.Cancel
                         title: qsTr("Please input user password")

                         contentItem: Rectangle {
                             color: "#FFFFFF"
                             implicitHeight: 50
                             implicitWidth: 200

                             TextField {
                                 id: textFieldPswDelRoute
                                 anchors.centerIn: parent
                                 echoMode: TextInput.Password
                                 placeholderText: qsTr("Input user password")
                                 focus: true
                                 Keys.onReturnPressed: dialogDelRoute.accept()
                             }
                         }

                         onAccepted: {
                             if (textFieldPswDelRoute.text) {
                                 network.del_route(
                                     textFieldDestination.text,
                                     textFieldGenmask.text,
                                     textFieldPswDelRoute.text
                                 )
                             }
                         }
                     }

                     MyControls.Button {
                         text: qsTr("-")
                         implicitWidth: 40
                         onClicked: dialogDelRoute.open()
                     }
                 }
             }
         }
    }

    MyControls.GroupBox {
        id: groupBoxNetwork
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 16
        anchors.left: parent.left
        anchors.leftMargin: 196
        anchors.right: parent.right
        anchors.rightMargin: 16
        anchors.top: parent.top
        anchors.topMargin: 192

        Label {
            font.family: bold.font.family
            font.pixelSize: 16
            text: qsTr("Terminal Output")
        }
        MyControls.Button {
            anchors.right: parent.right
            anchors.top: parent.top
            text: qsTr("Clear")

            onClicked: textAreaNetwork.clear()
        }
        ScrollView {
            anchors.bottom: parent.bottom
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.topMargin: 54

            background: Rectangle {
                border.color: "#CAD0E0"
                radius: 8
            }

            TextArea {
                id: textAreaNetwork
                anchors.fill: parent
                font.family: medium.font.family
                font.pixelSize: 16
                readOnly: true
            }
        }
    }
}
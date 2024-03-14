import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import Controls as MyControls
import Components as MyComponents

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

        MyControls.TabButton {
            anchors.left: parent.left
            anchors.right: parent.right
            text: qsTr("Ethernet Priority")
        }
    }

    StackLayout {
        anchors.left: parent.left
        anchors.leftMargin: 196
        anchors.right: parent.right
        anchors.rightMargin: 16
        anchors.top: parent.top
        anchors.topMargin: 16
        anchors.bottom: terminalOutputNw.top
        anchors.bottomMargin: 16
        currentIndex: vertTabBarNetwork.currentIndex

        Network {
            id: network
            Component.onCompleted: network.Stdout.connect(terminalOutputNw.textArea.append)
        }

         MyControls.GroupBox {
             Layout.fillWidth: true
             height: 110

             Label {
                 font.family: bold.name
                 font.pixelSize: 16
                 text: qsTr("Telnet")
             }

             RowLayout {
                 anchors.horizontalCenter: parent.horizontalCenter
                 anchors.verticalCenter: parent.verticalCenter

                 Label {
                    font.family: bold.name
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
                    font.family: bold.name
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
                 font.family: bold.name
                 font.pixelSize: 16
                 text: qsTr("Route")
             }

             MyComponents.Dialog {
                 id: dialogAddRoute
                 onAction: {
                     network.add_route(
                         textFieldDestination.text,
                         textFieldGenmask.text,
                         textFieldGateway.text,
                         input
                     )
                 }
             }

             MyComponents.Dialog {
                 id: dialogDelRoute
                 onAction: {
                     network.del_route(
                         textFieldDestination.text,
                         textFieldGenmask.text,
                         input
                     )
                 }
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
                         font.family: bold.name
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
                         font.family: bold.name
                         font.pixelSize: 16
                         text: qsTr("Genmask")
                     }

                     MyControls.TextField {
                         id: textFieldGenmask
                         implicitWidth: 150
                         inputMethodHints: Qt.ImhDigitsOnly
                     }

                     Label {
                         font.family: bold.name
                         font.pixelSize: 16
                         text: qsTr("Gateway")
                     }

                     MyControls.TextField {
                         id: textFieldGateway
                         implicitWidth: 230
                         placeholderText: qsTr("Leave empty when deleting")
                         inputMethodHints: Qt.ImhDigitsOnly
                     }

                     MyControls.Button {
                         text: qsTr("+")
                         implicitWidth: 40
                         onClicked: dialogAddRoute.open()
                     }

                     MyControls.Button {
                         text: qsTr("-")
                         implicitWidth: 40
                         onClicked: dialogDelRoute.open()
                     }
                 }
             }
         }

         MyControls.GroupBox {
             Layout.fillWidth: true
             height: 110

             Label {
                 font.family: bold.name
                 font.pixelSize: 16
                 text: qsTr("Adjust Ethernet Priority")
             }

             RowLayout {
                 anchors.horizontalCenter: parent.horizontalCenter
                 anchors.verticalCenter: parent.verticalCenter

                MyControls.Button {
                    text: qsTr("One Key Adjust")
                    onClicked: {
                        network.adj_priority()
                    }
                }
             }
         }
    }

    MyComponents.TerminalOutput {
        id: terminalOutputNw
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 16
        anchors.left: parent.left
        anchors.leftMargin: 196
        anchors.right: parent.right
        anchors.rightMargin: 16
        anchors.top: parent.top
        anchors.topMargin: 192
    }
}
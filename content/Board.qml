import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Qt.labs.qmlmodels

import Controls as MyControls

import src.board


Item {
    TableModel {
        id: tableModel
    }

    MyControls.GroupBox {
        id: groupBoxBoard
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
            text: qsTr("Search")
        }

        RowLayout {
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.verticalCenter: parent.verticalCenter

            MyControls.Button {
                id: searchButton
                text: qsTr("Search Devices")
                onClicked: {
                    tableModel.discover()
                }
            }
        }
    }

    MyControls.GroupBox {
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 16
        anchors.left: parent.left
        anchors.leftMargin: 16
        anchors.right: parent.right
        anchors.rightMargin: 16
        anchors.top: groupBoxBoard.bottom
        anchors.topMargin: 16

        HorizontalHeaderView {
            id: horizontalHeader

            anchors.left: tableView.left
            anchors.top: parent.top
            clip: true
            syncView: tableView

            delegate: Rectangle {
                color: "#ECF0F5"
                implicitHeight: 50
                implicitWidth: 100

                Text {
                    anchors.centerIn: parent
                    font.family: bold.name
                    font.pixelSize: 16
                    text: display
                }
            }
        }
        TableView {
            id: tableView

            anchors.bottom: parent.bottom
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: horizontalHeader.bottom
            clip: true
            columnSpacing: 1
            delegate: chooser
            model: tableModel
            rowSpacing: 1

            selectionModel: ItemSelectionModel {
            }

            ScrollBar.horizontal: ScrollBar {
                policy: ScrollBar.AsNeeded
            }
            ScrollBar.vertical: ScrollBar {
                policy: ScrollBar.AsNeeded
            }

            DelegateChooser {
                id: chooser

                DelegateChoice {
                    column: 0

                    delegate: Rectangle {
                        implicitHeight: 50
                        implicitWidth: 130

                        Text {
                            anchors.centerIn: parent
                            font.family: medium.name
                            font.pixelSize: 16
                            text: display === undefined ? "NA" : display
                        }

                        TableView.editDelegate: TextField {
                            anchors.fill: parent
                            font.family: medium.name
                            font.pixelSize: 16
                            text: display
                            horizontalAlignment: TextInput.AlignHCenter
                            verticalAlignment: TextInput.AlignVCenter
                            TableView.onCommit: display = text
                            inputMethodHints: Qt.ImhDigitsOnly
                        }
                    }
                }
                DelegateChoice {
                    column: 1

                    delegate: Rectangle {
                        implicitWidth: 80
                        implicitHeight: 50

                        Text {
                            textFormat: Text.RichText
                            text: hyperlink ? "<a href='http://" + hyperlink + "'>" + qsTr("Home Page") + "</a>" : "-"
                            onLinkActivated: (link) => Qt.openUrlExternally(link)
                            anchors.centerIn: parent
                            font.family: medium.name
                            font.pixelSize: 16
                        }
                    }
                }
                DelegateChoice {
                    column: 2

                    delegate: Rectangle {
                        implicitHeight: 50
                        implicitWidth: 100

                        Text {
                            anchors.centerIn: parent
                            font.family: medium.name
                            font.pixelSize: 16
                            text: display === undefined ? "NA" : display
                        }
                    }
                }
                DelegateChoice {
                    column: 3

                    delegate: Rectangle {
                        implicitHeight: 50
                        implicitWidth: 140

                        Text {
                            anchors.centerIn: parent
                            font.family: medium.name
                            font.pixelSize: 16
                            text: display === undefined ? "NA" : display
                        }
                    }
                }
                DelegateChoice {
                    column: 4

                    delegate: Rectangle {
                        implicitHeight: 50
                        implicitWidth: 80

                        Text {
                            anchors.centerIn: parent
                            font.family: medium.name
                            font.pixelSize: 16
                            text: display === undefined ? "NA" : display
                        }
                    }
                }
                DelegateChoice {
                    column: 5

                    delegate: Rectangle {
                        implicitHeight: 50
                        implicitWidth: 130

                        Text {
                            anchors.centerIn: parent
                            font.family: medium.name
                            font.pixelSize: 16
                            text: display === undefined ? "NA" : display
                        }
                        TableView.editDelegate: TextField {
                            anchors.fill: parent
                            font.family: medium.name
                            font.pixelSize: 16
                            text: display
                            horizontalAlignment: TextInput.AlignHCenter
                            verticalAlignment: TextInput.AlignVCenter
                            TableView.onCommit: display = text
                            inputMethodHints: Qt.ImhDigitsOnly
                        }
                    }
                }
                DelegateChoice {
                    column: 6

                    delegate: Rectangle {
                        implicitHeight: 50
                        implicitWidth: 130

                        Text {
                            anchors.centerIn: parent
                            font.family: medium.name
                            font.pixelSize: 16
                            text: display === undefined ? "NA" : display
                        }
                        TableView.editDelegate: TextField {
                            anchors.fill: parent
                            font.family: medium.name
                            font.pixelSize: 16
                            text: display
                            horizontalAlignment: TextInput.AlignHCenter
                            verticalAlignment: TextInput.AlignVCenter
                            TableView.onCommit: display = text
                            inputMethodHints: Qt.ImhDigitsOnly
                        }
                    }
                }
                DelegateChoice {
                    column: 7

                    delegate: Rectangle {
                        implicitHeight: 50
                        implicitWidth: 120

                        MyControls.ComboBox {
                            anchors.centerIn: parent
                            implicitHeight: 40
                            implicitWidth: 110
                            model: [
                                {"value": 0, "text": qsTr("DHCP")},
                                {"value": 128, "text": qsTr("Static")}
                            ]
                            textRole: "text"
                            valueRole: "value"
                            Component.onCompleted: currentIndex = indexOfValue(display[6])
                            onActivated: tableModel.setDhcp(display, currentValue)
                        }
                    }
                }
                DelegateChoice {
                    column: 8

                    delegate: Rectangle {
                        implicitHeight: 50
                        implicitWidth: 130

                        Text {
                            anchors.centerIn: parent
                            font.family: medium.name
                            font.pixelSize: 16
                            text: display === undefined ? "NA" : display
                        }
                        TableView.editDelegate: TextField {
                            anchors.fill: parent
                            font.family: medium.name
                            font.pixelSize: 16
                            text: display
                            horizontalAlignment: TextInput.AlignHCenter
                            verticalAlignment: TextInput.AlignVCenter
                            TableView.onCommit: display = text
                            inputMethodHints: Qt.ImhDigitsOnly
                        }
                    }
                }
                DelegateChoice {
                    column: 9

                    delegate: Rectangle {
                        implicitHeight: 50
                        implicitWidth: 80

                        Text {
                            anchors.centerIn: parent
                            font.family: medium.name
                            font.pixelSize: 16
                            text: display === undefined ? "NA" : display
                        }
                        TableView.editDelegate: TextField {
                            anchors.fill: parent
                            font.family: medium.name
                            font.pixelSize: 16
                            text: display
                            horizontalAlignment: TextInput.AlignHCenter
                            verticalAlignment: TextInput.AlignVCenter
                            TableView.onCommit: display = text
                            inputMethodHints: Qt.ImhDigitsOnly
                        }
                    }
                }
                DelegateChoice {
                    column: 10

                    delegate: Rectangle {
                        implicitHeight: 50
                        implicitWidth: 100

                        MyControls.Button {
                            anchors.centerIn: parent
                            implicitHeight: 40
                            implicitWidth: 90
                            text: qsTr("Reboot")

                            onClicked: {
                                tableModel.reboot(embbutton);
                            }
                        }
                    }
                }
            }
        }
    }
}
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Qt.labs.qmlmodels

import Controls as MyControls

import src.nvr


Item {
    HikTableModel {
        id: hikTableModel
    }

    function statusBar(text) {
        labelStatusBar.text = qsTr(text)
        drawerStatusBar.open()
    }

    Inti {
        id: inti
        Component.onCompleted: inti.output.connect(statusBar)
    }

    MyControls.GroupBox {
        id: groupBoxNvr
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
                id: searchNvrButton
                text: qsTr("Search NVR & IPC")
                onClicked: {
                    hikTableModel.discover()
                    labelDrawer.text = qsTr("* Please ensure there is only one NVR in the LAN, and IPC should be initialized one by one.")
                    drawer.open()
                    timer.running = true
                }
            }

            ToolSeparator {
                rightPadding: 3
                leftPadding: 3
                bottomPadding: 0
                topPadding: 0
                Layout.fillHeight: true
            }

            Label {
                font.family: bold.name
                font.pixelSize: 16
                text: qsTr("Set number of IPC:")
            }

            MyControls.ComboBox {
                id: comboBoxIpcNum
                implicitWidth: 100
                model: [1, 2, 3, 4, 5, 6, 7, 8]
                onActivated: inti.ipcIpGenerator(currentValue)
            }

            MyControls.Button {
                id: initNvrButton
                text: qsTr("Initialize NVR")
                onClicked: inti.initNvr()
            }

            ToolSeparator {
                rightPadding: 3
                leftPadding: 3
                bottomPadding: 0
                topPadding: 0
                Layout.fillHeight: true
            }

            MyControls.Button {
                id: initIpcButton
                text: qsTr("Initialize IPC")
                onClicked: inti.initIpc()
            }

            ToolSeparator {
                rightPadding: 3
                leftPadding: 3
                bottomPadding: 0
                topPadding: 0
                Layout.fillHeight: true
            }

            MyControls.Button {
                id: cfgChnButton
                text: qsTr("Configure Channels")
                onClicked: inti.configChannel(comboBoxIpcNum.currentValue)
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
        anchors.top: groupBoxNvr.bottom
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
            model: hikTableModel
            rowSpacing: 1

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
                        implicitWidth: 170

                        Text {
                            anchors.centerIn: parent
                            font.family: medium.name
                            font.pixelSize: 16
                            text: display === undefined ? "NA" : display
                        }
                    }
                }
                DelegateChoice {
                    column: 1

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
                    column: 2

                    delegate: Rectangle {
                        implicitHeight: 50
                        implicitWidth: 120

                        Text {
                            textFormat: Text.RichText
                            text: "<a href='http://" + hyperlink + "'>" + hyperlink + "</a>"
                            onLinkActivated: (link) => Qt.openUrlExternally(link)
                            anchors.centerIn: parent
                            font.family: medium.name
                            font.pixelSize: 16
                        }
                    }
                }
                DelegateChoice {
                    column: 3

                    delegate: Rectangle {
                        implicitHeight: 50
                        implicitWidth: 120

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
                        implicitWidth: 120

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
                        implicitWidth: 200

                        Text {
                            anchors.centerIn: parent
                            font.family: medium.name
                            font.pixelSize: 16
                            text: display === undefined ? "NA" : display
                        }
                    }
                }
                DelegateChoice {
                    column: 6

                    delegate: Rectangle {
                        implicitHeight: 50
                        implicitWidth: 200

                        Text {
                            anchors.centerIn: parent
                            font.family: medium.name
                            font.pixelSize: 16
                            text: display === undefined ? "NA" : display
                        }
                    }
                }
            }
        }
    }
}
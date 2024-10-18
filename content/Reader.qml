import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs

import Controls as MyControls
import Components as MyComponents

import src.reader
import src.reader.rongrui


Item {
    MyControls.VertTabBar {
        id: vertTabBarRfid
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.top: parent.top
        width: 180

        MyControls.TabButton {
            anchors.left: parent.left
            anchors.right: parent.right
            text: qsTr("Rong Rui Reader")
        }

        MyControls.TabButton {
            anchors.left: parent.left
            anchors.right: parent.right
            text: qsTr("Hong Lu Reader")
        }
    }

    StackLayout {
        anchors.left: parent.left
        anchors.leftMargin: 196
        anchors.right: parent.right
        anchors.rightMargin: 16
        anchors.top: parent.top
        anchors.topMargin: 16
        anchors.bottom: terminalOutputRd.top
        anchors.bottomMargin: 16
        currentIndex: vertTabBarRfid.currentIndex

        Reader {
            id: reader
            Component.onCompleted: reader.Stdout.connect(terminalOutputRd.textArea.append)
        }

        ReaderRongRui {
            id: readerRongRui
            Component.onCompleted: readerRongRui.Response.connect(terminalOutputRd.textArea.append)
        }

        MyControls.GroupBox {
            Layout.fillWidth: true
            height: 110

            Label {
                font.family: bold.name
                font.pixelSize: 16
                text: qsTr("Operation")
            }

            RowLayout {
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.verticalCenter: parent.verticalCenter

                Label {
                    font.family: bold.name
                    font.pixelSize: 16
                    text: qsTr("Serial Port")
                }

                MyControls.ComboBox {
                    id: comboBoxRfidPort
                    model: readerRongRui.availablePorts
                    enabled: ! switchRfid.checked
                    // currentIndex: -1
                    popup.onOpened: readerRongRui.availablePorts = readerRongRui.update_ports()
                }

                Label {
                    font.family: bold.name
                    font.pixelSize: 16
                    text: qsTr("Baud Rate")
                }

                MyControls.ComboBox {
                    id: comboBoxRfidBaudRate
                    model: readerRongRui.baudRates
                    enabled: ! switchRfid.checked
                    Component.onCompleted: currentIndex = indexOfValue(19200)
                }

                Label {
                    font.family: bold.name
                    font.pixelSize: 16
                    text: qsTr("Open Serial Port")
                }

                MyControls.Switch {
                    id: switchRfid
                    onCheckedChanged: {
                        checked ? readerRongRui.openSerialPort(comboBoxRfidPort.currentValue, comboBoxRfidBaudRate.currentValue) : readerRongRui.closeSerialPort()
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
                    text: qsTr("Open TCP")
                }

                MyControls.Switch {
                    id: switchReaderRongRui
                    onCheckedChanged: {
                        checked ? readerRongRui.open() : readerRongRui.close()
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
                    text: qsTr("Open RF")
                }

                MyControls.Switch {
                    id: switchReaderRongRui1
                    onCheckedChanged: {
                        checked ? readerRongRui.openRF() : readerRongRui.closeRF()
                    }
                }

                MyControls.Button {
                    text: qsTr("Check Inventory")
                    onClicked: {
                        readerRongRui.checkInventory()
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
                text: qsTr("Terminal Input")
            }

            RowLayout {
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.verticalCenter: parent.verticalCenter

                MyControls.Button {
                    text: qsTr("Start configuration")
                    onClicked: reader.start_config()
                }

                MyControls.Button {
                    text: qsTr("Quit")
                    onClicked: reader.write("q")
                }

                ToolSeparator {
                    rightPadding: 3
                    leftPadding: 3
                    bottomPadding: 0
                    topPadding: 0
                    Layout.fillHeight: true
                }

                MyControls.TextField {
                    id: textFieldKeyData
                    implicitWidth: 300
                    Keys.onReturnPressed: btnSend.clicked()
                }

                MyControls.Button {
                    id: btnSend
                    text: qsTr("Send")
                    onClicked: {
                        reader.write(textFieldKeyData.text)
                        textFieldKeyData.clear()
                    }
                }

                ToolSeparator {
                    rightPadding: 3
                    leftPadding: 3
                    bottomPadding: 0
                    topPadding: 0
                    Layout.fillHeight: true
                }

                FolderDialog {
                    id: folderDialogRd
                    title: qsTr("Please select a folder to save records")
                    currentFolder: "/media"
                    acceptLabel: qsTr("Save")
                    onAccepted: {
                        reader.record(selectedFolder, terminalOutputRd.textArea.text)
                    }
                }

                MyControls.Button {
                    text: qsTr("Save to...")
                    onClicked: folderDialogRd.open()
                }
            }
        }
    }

    MyComponents.TerminalOutput {
        id: terminalOutputRd
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
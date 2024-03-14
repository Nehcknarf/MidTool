import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs

import Controls as MyControls
import Components as MyComponents

import src.maintenance


Item {
    MyControls.VertTabBar {
        id: vertTabBarDeploy
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.top: parent.top
        width: 180

        MyControls.TabButton {
            anchors.left: parent.left
            anchors.right: parent.right
            text: qsTr("Install")
        }

        MyControls.TabButton {
            anchors.left: parent.left
            anchors.right: parent.right
            text: qsTr("Update")
        }

        MyControls.TabButton {
            anchors.left: parent.left
            anchors.right: parent.right
            text: qsTr("Restore")
        }
    }

    StackLayout {
        anchors.bottom: terminalOutputMt.top
        anchors.bottomMargin: 16
        anchors.left: parent.left
        anchors.leftMargin: 196
        anchors.right: parent.right
        anchors.rightMargin: 16
        anchors.top: parent.top
        anchors.topMargin: 16
        currentIndex: vertTabBarDeploy.currentIndex

        Maintenance {
            id: maintenance
            Component.onCompleted: maintenance.Stdout.connect(terminalOutputMt.textArea.append)
        }

        MyControls.GroupBox {
            Layout.fillHeight: true
            Layout.fillWidth: true
            height: 110

            Label {
                font.family: bold.name
                font.pixelSize: 16
                text: qsTr("New installation (For factory)")
            }

            RowLayout {
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.verticalCenter: parent.verticalCenter

                Label {
                    font.family: bold.name
                    font.pixelSize: 16
                    text: qsTr("Select the type of consumable cabinet")
                }

                MyControls.ComboBox {
                    id: comboBoxCabinet
                    model: maintenance.cabinets
                    // textRole: "text"
                    // valueRole: "value"
                    // currentIndex: -1
                }

                MyControls.Button {
                    text: qsTr("Install")
                    onClicked: {
                        maintenance.install_middleware(comboBoxCabinet.currentValue)
                        // console.log(comboBoxCabinet.currentValue)
                    }
                }
            }
        }

        MyControls.GroupBox {
            Layout.fillHeight: true
            Layout.fillWidth: true
            height: 110

            Label {
                font.family: bold.name
                font.pixelSize: 16
                text: qsTr("Update (For Implementation Engineer)")
            }

            RowLayout {
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.verticalCenter: parent.verticalCenter

                FileDialog {
                    id: fileDialogUpdate
                    currentFolder: "/media"
                    nameFilters: [qsTr("Update package (*.tar.gz)")]
                    title: qsTr("Please select middleware update package")

                    onAccepted: {
                        terminalOutputMt.textArea.append(selectedFile)
                        maintenance.update_middleware(selectedFile)
                    }
                }

                MyControls.Button {
                    text: qsTr("Select update package...")
                    onClicked: fileDialogUpdate.open()
                }

                // MyControls.Button {
                //     text: qsTr("Execute update")
                //     onClicked: {
                //         maintenance.update_middleware(fileDialogUpdate.selectedFile)
                //         // console.log(comboBoxCabinet.currentValue)
                //     }
                // }
            }
        }

        MyControls.GroupBox {
            Layout.fillHeight: true
            Layout.fillWidth: true
            height: 110

            Label {
                font.family: bold.name
                font.pixelSize: 16
                text: qsTr("Backup restore")
            }

            RowLayout {
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.verticalCenter: parent.verticalCenter

                Label {
                    font.family: bold.name
                    font.pixelSize: 16
                    text: qsTr("Select a middleware backup")
                }

                MyControls.ComboBox {
                    id: comboBoxBackUp
                    model: maintenance.backups
                    // currentIndex: -1
                }

                MyControls.Button {
                    text: qsTr("Restore")
                    onClicked: {
                        maintenance.restore_middleware(comboBoxBackUp.currentText)
                    }
                }
            }
        }
    }

     MyComponents.TerminalOutput {
        id: terminalOutputMt
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
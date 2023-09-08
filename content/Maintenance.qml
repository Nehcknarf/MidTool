import QtQuick 6.5
import QtQuick.Controls 6.5
import QtQuick.Layouts 6.5
import QtQuick.Dialogs 6.5

import Controls as MyControls

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
        anchors.bottom: groupBoxDeploy.top
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
            Component.onCompleted: maintenance.Stdout.connect(textAreaMaintenance.append)
        }
        MyControls.GroupBox {
            Layout.fillHeight: true
            Layout.fillWidth: true
            height: 110

            Label {
                font.bold: true
                font.pixelSize: 16
                text: qsTr("New installation (For factory)")
            }
            RowLayout {
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.verticalCenter: parent.verticalCenter

                Label {
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
                        maintenance.install_middleware(comboBoxCabinet.currentValue);
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
                font.bold: true
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
                        textAreaMaintenance.append(selectedFile);
                        // maintenance.update_middleware(selectedFile)
                    }
                }
                MyControls.Button {
                    text: qsTr("Select update package")

                    onClicked: fileDialogUpdate.open()
                }
                MyControls.Button {
                    text: qsTr("Execute update")

                    onClicked: {
                        maintenance.update_middleware(fileDialogUpdate.selectedFile);
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
                font.bold: true
                font.pixelSize: 16
                text: qsTr("Backup restore")
            }

            RowLayout {
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.verticalCenter: parent.verticalCenter

                Label {
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
                        maintenance.update_middleware(comboBoxBackUp.currentText)
                    }
                }
            }
        }
    }
    MyControls.GroupBox {
        id: groupBoxDeploy

        anchors.bottom: parent.bottom
        anchors.bottomMargin: 16
        anchors.left: parent.left
        anchors.leftMargin: 196
        anchors.right: parent.right
        anchors.rightMargin: 16
        anchors.top: parent.top
        anchors.topMargin: 192

        Label {
            font.bold: true
            font.pixelSize: 16
            text: qsTr("Terminal Output")
        }
        MyControls.Button {
            anchors.right: parent.right
            anchors.top: parent.top
            text: qsTr("Clear")

            onClicked: textAreaMaintenance.clear()
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
                id: textAreaMaintenance

                anchors.fill: parent
                readOnly: true
            }
        }
    }
}
import QtQuick 6.5
import QtQuick.Controls 6.5
import QtQuick.Layouts 6.5

import Controls as MyControls

import src.process


Item {
    MyControls.VertTabBar {
        id: vertTabBarTime
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.top: parent.top
        width: 180

        MyControls.TabButton {
            anchors.left: parent.left
            anchors.right: parent.right
            text: qsTr("Time/Timezone")
        }

        MyControls.TabButton {
            anchors.left: parent.left
            anchors.right: parent.right
            text: qsTr("NTP Server")
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

        Process {
            id: processMaintenance
            Component.onCompleted: processMaintenance.Stdout.connect(textAreaDeploy.append)
        }

        MyControls.GroupBox {
            Layout.fillHeight: true
            Layout.fillWidth: true
            height: 110

            Label {
                font.bold: true
                font.pixelSize: 16
                text: qsTr("Settings")
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
                    // currentIndex: -1
                }
                MyControls.Button {
                    text: qsTr("Install")

                    onClicked: {
                        processMaintenance.install_middleware(comboBoxCabinet.currentValue);
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
                        textAreaDeploy.append(selectedFile);
                        // processMaintenance.update_middleware(selectedFile)
                    }
                }
                MyControls.Button {
                    text: qsTr("Select update package first")

                    onClicked: fileDialogUpdate.open()
                }
                MyControls.Button {
                    text: qsTr("Execute update")

                    onClicked: {
                        processMaintenance.update_middleware(fileDialogUpdate.selectedFile);
                        // console.log(comboBoxCabinet.currentValue)
                    }
                }
            }
        }
    }
}
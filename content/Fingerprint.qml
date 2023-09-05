import QtQuick 6.5
import QtQuick.Controls 6.5
import QtQuick.Layouts 6.5
import QtQuick.Dialogs 6.5

import Controls as MyControls

import src.fingerprint


Item {
    MyControls.VertTabBar {
        id: vertTabBarFingerprint

        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.top: parent.top
        width: 180

        MyControls.TabButton {
            anchors.left: parent.left
            anchors.right: parent.right
            text: qsTr("Square Fingerprint")
        }
        MyControls.TabButton {
            anchors.left: parent.left
            anchors.right: parent.right
            text: qsTr("Round Fingerprint")
        }
    }
    StackLayout {
        id: stackLayout

        anchors.bottom: groupBoxFPOutput.top
        anchors.bottomMargin: 16
        anchors.left: parent.left
        anchors.leftMargin: 196
        anchors.right: parent.right
        anchors.rightMargin: 16
        anchors.top: parent.top
        anchors.topMargin: 16
        currentIndex: vertTabBarFingerprint.currentIndex

        Rectangle {
            color: "transparent"

            SquareFingerPrint {
                id: squareFingerPrint

                Component.onCompleted: squareFingerPrint.Output.connect(textAreaFingerprint.append)
            }
            MyControls.GroupBox {
                id: groupBoxConfigS

                anchors.bottom: parent.bottom
                anchors.left: parent.left
                anchors.top: parent.top
                height: 160
                width: 500

                Label {
                    font.bold: true
                    font.pixelSize: 16
                    text: qsTr("Config")
                }
                GridLayout {
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.verticalCenter: parent.verticalCenter
                    columns: 4
                    rows: 2

                    Label {
                        font.pixelSize: 16
                        text: qsTr("Serial Port")
                    }
                    MyControls.ComboBox {
                        id: comboBoxComS

                        model: squareFingerPrint.coms
                        // currentIndex: -1
                    }
                     Label {
                        font.pixelSize: 16
                        text: qsTr("Connect")
                    }
                    MyControls.Switch {
                        onCheckedChanged: {
                            if (checked) {
                                let ret = squareFingerPrint.open_device(comboBoxComS.currentValue, comboBoxBaudRateS.currentValue);
                                console.log("library return:", ret);
                            } else {
                                let ret = squareFingerPrint.close_device();
                                console.log("library return:", ret);
                            }
                        }
                    }
                    Label {
                        font.pixelSize: 16
                        text: qsTr("Baud Rate")
                    }
                    MyControls.ComboBox {
                        id: comboBoxBaudRateS

                        model: squareFingerPrint.baud_rates
                        // currentIndex: -1
                    }
                }
            }
            MyControls.GroupBox {
                anchors.bottom: parent.bottom
                anchors.left: groupBoxConfigS.right
                anchors.leftMargin: 16
                anchors.right: parent.right
                anchors.top: parent.top
                height: 160

                // Label {
                //     font.bold: true
                //     font.pixelSize: 16
                //     text: qsTr("Function")
                // }
                GridLayout {
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.verticalCenter: parent.verticalCenter
                    columns: 2
                    rows: 3

                    Dialog {
                        id: dialogSet

                        modal: true
                        standardButtons: Dialog.Ok | Dialog.Cancel
                        title: "Please input an integer from 1 to 1049."

                        contentItem: Rectangle {
                            color: "#FFFFFF"
                            implicitHeight: 50
                            implicitWidth: 200

                            TextField {
                                id: textFieldSetID

                                anchors.centerIn: parent
                                placeholderText: qsTr("Input an integer")
                            }
                        }

                        onAccepted: {
                            if (textFieldSetID.text) {
                                squareFingerPrint.get_fingerprint(textFieldSetID.text);
                            }
                        }
                    }
                    MyControls.Button {
                        text: qsTr("Collect Fingerprint")

                        onClicked: dialogSet.open()
                    }
                    Dialog {
                        id: dialogDelS

                        modal: true
                        standardButtons: Dialog.Ok | Dialog.Cancel
                        title: "Please input an integer from 1 to 1049."

                        contentItem: Rectangle {
                            color: "#FFFFFF"
                            implicitHeight: 50
                            implicitWidth: 200

                            TextField {
                                id: textFieldDelIDS

                                anchors.centerIn: parent
                                placeholderText: qsTr("Input an integer")
                            }
                        }

                        onAccepted: {
                            if (textFieldDelIDS.text) {
                                squareFingerPrint.del_flash(textFieldDelIDS.text);
                            }
                        }
                    }
                    MyControls.Button {
                        text: qsTr("Delete Specific Fingerprint")

                        onClicked: dialogDelS.open()
                    }
                    MyControls.Button {
                        text: qsTr("Search Fingerprint")

                        onClicked: squareFingerPrint.search_fingerprint()
                    }
                    MyControls.Button {
                        text: qsTr("Delete All Fingerprints")

                        onClicked: squareFingerPrint.clean_flash()
                    }
                    MyControls.Button {
                        text: qsTr("Count Fingerprints")

                        onClicked: squareFingerPrint.get_template_num()
                    }
                }
            }
        }
        Rectangle {
            color: "transparent"

            RoundFingerPrint {
                id: roundFingerPrint

                Component.onCompleted: roundFingerPrint.Output.connect(textAreaFingerprint.append)
            }
            MyControls.GroupBox {
                id: groupBoxConfigR

                anchors.bottom: parent.bottom
                anchors.left: parent.left
                anchors.top: parent.top
                height: 160
                width: 500

                Label {
                    font.bold: true
                    font.pixelSize: 16
                    text: qsTr("Config")
                }
                GridLayout {
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.verticalCenter: parent.verticalCenter
                    columns: 4
                    rows: 2

                    Label {
                        font.pixelSize: 16
                        text: qsTr("Serial Port")
                    }
                    MyControls.ComboBox {
                        id: comboBoxComR

                        model: roundFingerPrint.coms
                        // currentIndex: -1
                        textRole: "text"
                        valueRole: "value"
                    }
                    Label {
                        font.pixelSize: 16
                        text: qsTr("Connect")
                    }
                    MyControls.Switch {
                        onCheckedChanged: {
                            if (checked) {
                                let ret = roundFingerPrint.open_device(comboBoxComR.currentValue, comboBoxBaudRateR.currentValue);
                                console.log("library return:", ret);
                            } else {
                                let ret = roundFingerPrint.close_device();
                                console.log("library return:", ret);
                            }
                        }
                    }
                    Label {
                        font.pixelSize: 16
                        text: qsTr("Baud Rate")
                    }
                    MyControls.ComboBox {
                        id: comboBoxBaudRateR

                        model: roundFingerPrint.baud_rates
                        // currentIndex: -1
                    }
                }
            }
            MyControls.GroupBox {
                anchors.bottom: parent.bottom
                anchors.left: groupBoxConfigR.right
                anchors.leftMargin: 16
                anchors.right: parent.right
                anchors.top: parent.top
                height: 160

                // Label {
                //     font.bold: true
                //     font.pixelSize: 16
                //     text: qsTr("Function")
                // }
                GridLayout {
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.verticalCenter: parent.verticalCenter
                    columns: 2
                    rows: 2

                    MyControls.Button {
                        text: qsTr("Collect Fingerprint")

                        onClicked: roundFingerPrint.get_fingerprint()
                    }
                    Dialog {
                        id: dialogDelR

                        modal: true
                        standardButtons: Dialog.Ok | Dialog.Cancel
                        title: "Please input an integer from 1 to 500."

                        contentItem: Rectangle {
                            color: "#FFFFFF"
                            implicitHeight: 50
                            implicitWidth: 200

                            TextField {
                                id: textFieldDelIDR

                                anchors.centerIn: parent
                                placeholderText: qsTr("Input an integer")
                            }
                        }

                        onAccepted: {
                            if (textFieldDelIDR.text) {
                                roundFingerPrint.del_flash(textFieldDelIDR.text);
                            }
                        }
                    }
                    MyControls.Button {
                        text: qsTr("Delete Specific Fingerprint")

                        onClicked: dialogDelR.open()
                    }
                    MyControls.Button {
                        text: qsTr("Search Fingerprint")

                        onClicked: roundFingerPrint.search_fingerprint()
                    }
                    MyControls.Button {
                        text: qsTr("Delete All Fingerprints")

                        onClicked: roundFingerPrint.clean_flash()
                    }
                }
            }
        }
    }
    MyControls.GroupBox {
        id: groupBoxFPOutput

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

            onClicked: textAreaFingerprint.clear()
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
                id: textAreaFingerprint

                anchors.fill: parent
                readOnly: true
            }
        }
    }
}
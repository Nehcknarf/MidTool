import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import Controls as MyControls
import Components as MyComponents

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

        MyControls.TabButton {
            anchors.left: parent.left
            anchors.right: parent.right
            text: qsTr("ZA300 Fingerprint")
        }
    }

    StackLayout {
        id: stackLayout
        anchors.bottom: terminalOutputFp.top
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
                Component.onCompleted: squareFingerPrint.output.connect(terminalOutputFp.textArea.append)
            }

            MyControls.GroupBox {
                id: groupBoxConfigS
                anchors.bottom: parent.bottom
                anchors.left: parent.left
                anchors.top: parent.top
                height: 160
                width: 500

                Label {
                    font.family: bold.name
                    font.pixelSize: 16
                    text: qsTr("Config")
                }

                GridLayout {
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.verticalCenter: parent.verticalCenter
                    columns: 4
                    rows: 2

                    Label {
                        font.family: bold.name
                        font.pixelSize: 16
                        text: qsTr("Serial Port")
                    }

                    MyControls.ComboBox {
                        id: comboBoxComS
                        model: squareFingerPrint.availablePorts
                        enabled: ! switchSquareFingerPrint.checked
                        // currentIndex: -1
                        popup.onOpened: squareFingerPrint.availablePorts = squareFingerPrint.update_ports()
                    }

                     Label {
                        font.family: bold.name
                        font.pixelSize: 16
                        text: qsTr("Connect")
                    }

                    MyControls.Switch {
                        id: switchSquareFingerPrint
                        onCheckedChanged: {
                            if (checked) {
                                let ret = squareFingerPrint.open_device(comboBoxComS.currentValue, comboBoxBaudRateS.currentValue)
                                if (ret !== 0) {
                                    switchSquareFingerPrint.checked = false
                                }
                            } else {
                                let ret = squareFingerPrint.close_device()
                            }
                        }
                    }

                    Label {
                        font.family: bold.name
                        font.pixelSize: 16
                        text: qsTr("Baud Rate")
                    }

                    MyControls.ComboBox {
                        id: comboBoxBaudRateS
                        model: squareFingerPrint.baudRates
                        enabled: ! switchSquareFingerPrint.checked
                        Component.onCompleted: currentIndex = indexOfValue(57600)
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

                Label {
                    font.family: bold.name
                    font.pixelSize: 16
                    text: qsTr("Func.")
                }

                MyComponents.Dialog {
                    id: dialogSet
                    title: qsTr("Please input an integer from 1 to 1049.")
                    placeholder: qsTr("Input an integer")
                    echoMode: TextInput.Normal
                    inputMethodHints: Qt.ImhDigitsOnly
                    onAction: {
                        squareFingerPrint.get_fingerprint(input)
                    }
                }

                MyComponents.Dialog {
                    id: dialogDelS
                    title: qsTr("Please input an integer from 1 to 1049.")
                    placeholder: qsTr("Input an integer")
                    echoMode: TextInput.Normal
                    inputMethodHints: Qt.ImhDigitsOnly
                    onAction: {
                        squareFingerPrint.del_flash(input)
                    }
                }

                GridLayout {
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.verticalCenter: parent.verticalCenter
                    columns: 2
                    rows: 3

                    MyControls.Button {
                        text: qsTr("Collect Fingerprint")
                        enabled: switchSquareFingerPrint.checked
                        onClicked: dialogSet.open()
                    }

                    MyControls.Button {
                        text: qsTr("Delete Specific Fingerprint")
                        enabled: switchSquareFingerPrint.checked
                        onClicked: dialogDelS.open()
                    }

                    MyControls.Button {
                        text: qsTr("Search Fingerprint")
                        enabled: switchSquareFingerPrint.checked
                        onClicked: squareFingerPrint.search_fingerprint()
                    }

                    MyControls.Button {
                        text: qsTr("Delete All Fingerprints")
                        enabled: switchSquareFingerPrint.checked
                        onClicked: squareFingerPrint.clean_flash()
                    }

                    MyControls.Button {
                        text: qsTr("Count Fingerprints")
                        enabled: switchSquareFingerPrint.checked
                        onClicked: squareFingerPrint.get_template_num()
                    }
                }
            }
        }

        Rectangle {
            color: "transparent"

            RoundFingerPrint {
                id: roundFingerPrint
                Component.onCompleted: roundFingerPrint.output.connect(terminalOutputFp.textArea.append)
            }

            MyControls.GroupBox {
                id: groupBoxConfigR
                anchors.bottom: parent.bottom
                anchors.left: parent.left
                anchors.top: parent.top
                height: 160
                width: 500

                Label {
                    font.family: bold.name
                    font.pixelSize: 16
                    text: qsTr("Config")
                }

                GridLayout {
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.verticalCenter: parent.verticalCenter
                    columns: 4
                    rows: 2

                    Label {
                        font.family: bold.name
                        font.pixelSize: 16
                        text: qsTr("Serial Port")
                    }

                    MyControls.ComboBox {
                        id: comboBoxComR
                        model: roundFingerPrint.availablePorts
                        enabled: ! switchRoundFingerPrint.checked
                        // currentIndex: -1
                        textRole: "text"
                        valueRole: "value"
                        popup.onOpened: roundFingerPrint.availablePorts = roundFingerPrint.update_ports()
                    }

                    Label {
                        font.family: bold.name
                        font.pixelSize: 16
                        text: qsTr("Connect")
                    }

                    MyControls.Switch {
                        id: switchRoundFingerPrint
                        onCheckedChanged: {
                            if (checked) {
                                let ret = roundFingerPrint.open_device(comboBoxComR.currentValue, comboBoxBaudRateR.currentValue)
                                if (ret !== 0) {
                                    switchRoundFingerPrint.checked = false
                                }
                            } else {
                                let ret = roundFingerPrint.close_device()
                            }
                        }
                    }

                    Label {
                        font.family: bold.name
                        font.pixelSize: 16
                        text: qsTr("Baud Rate")
                    }

                    MyControls.ComboBox {
                        id: comboBoxBaudRateR
                        model: roundFingerPrint.baudRates
                        enabled: ! switchRoundFingerPrint.checked
                        Component.onCompleted: currentIndex = indexOfValue(57600)
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

                Label {
                    font.family: bold.name
                    font.pixelSize: 16
                    text: qsTr("Func.")
                }

                MyComponents.Dialog {
                    id: dialogDelR
                    title: qsTr("Please input an integer from 1 to 500.")
                    placeholder: qsTr("Input an integer")
                    echoMode: TextInput.Normal
                    inputMethodHints: Qt.ImhDigitsOnly
                    onAction: {
                        roundFingerPrint.del_flash(input)
                    }
                }

                GridLayout {
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.verticalCenter: parent.verticalCenter
                    columns: 2
                    rows: 2

                    MyControls.Button {
                        text: qsTr("Collect Fingerprint")
                        enabled: switchRoundFingerPrint.checked
                        onClicked: roundFingerPrint.get_fingerprint()
                    }

                    MyControls.Button {
                        text: qsTr("Delete Specific Fingerprint")
                        enabled: switchRoundFingerPrint.checked
                        onClicked: dialogDelR.open()
                    }

                    MyControls.Button {
                        text: qsTr("Search Fingerprint")
                        enabled: switchRoundFingerPrint.checked
                        onClicked: roundFingerPrint.search_fingerprint()
                    }

                    MyControls.Button {
                        text: qsTr("Delete All Fingerprints")
                        enabled: switchRoundFingerPrint.checked
                        onClicked: roundFingerPrint.clean_flash()
                    }
                }
            }
        }

        Rectangle {
            color: "transparent"

            Za300FingerPrint {
                id: za300FingerPrint
                Component.onCompleted: za300FingerPrint.output.connect(terminalOutputFp.textArea.append)
            }

            MyControls.GroupBox {
                id: groupBoxConfigZ
                anchors.bottom: parent.bottom
                anchors.left: parent.left
                anchors.top: parent.top
                height: 160
                width: 500

                Label {
                    font.family: bold.name
                    font.pixelSize: 16
                    text: qsTr("Config")
                }

                GridLayout {
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.verticalCenter: parent.verticalCenter
                    columns: 4
                    rows: 2

                    Label {
                        font.family: bold.name
                        font.pixelSize: 16
                        text: qsTr("Serial Port")
                    }

                    MyControls.ComboBox {
                        id: comboBoxComZ
                        model: za300FingerPrint.availablePorts
                        enabled: ! switchZa300FingerPrint.checked
                        // currentIndex: -1
                        textRole: "text"
                        valueRole: "value"
                        popup.onOpened: za300FingerPrint.availablePorts = za300FingerPrint.update_ports()
                    }

                    Label {
                        font.family: bold.name
                        font.pixelSize: 16
                        text: qsTr("Connect")
                    }

                    MyControls.Switch {
                        id: switchZa300FingerPrint
                        onCheckedChanged: {
                            if (checked) {
                                let ret = za300FingerPrint.open_device(comboBoxComZ.currentValue, comboBoxBaudRateZ.currentValue)
                                if (ret !== 0) {
                                    switchZa300FingerPrint.checked = false
                                }
                            } else {
                                let ret = za300FingerPrint.close_device()
                            }
                        }
                    }

                    Label {
                        font.family: bold.name
                        font.pixelSize: 16
                        text: qsTr("Baud Rate")
                    }

                    MyControls.ComboBox {
                        id: comboBoxBaudRateZ
                        model: za300FingerPrint.baudRates
                        enabled: ! switchZa300FingerPrint.checked
                        Component.onCompleted: currentIndex = indexOfValue(57600)
                    }
                }
            }

            MyControls.GroupBox {
                anchors.bottom: parent.bottom
                anchors.left: groupBoxConfigZ.right
                anchors.leftMargin: 16
                anchors.right: parent.right
                anchors.top: parent.top
                height: 160

                Label {
                    font.family: bold.name
                    font.pixelSize: 16
                    text: qsTr("Func.")
                }

                MyComponents.Dialog {
                    id: dialogDelZ
                    title: qsTr("Please input an integer from 1 to 500.")
                    placeholder: qsTr("Input an integer")
                    echoMode: TextInput.Normal
                    inputMethodHints: Qt.ImhDigitsOnly
                    onAction: {
                        za300FingerPrint.del_flash(input)
                    }
                }

                GridLayout {
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.verticalCenter: parent.verticalCenter
                    columns: 2
                    rows: 2

                    MyControls.Button {
                        text: qsTr("Collect Fingerprint")
                        enabled: switchZa300FingerPrint.checked
                        onClicked: za300FingerPrint.get_fingerprint()
                    }

                    MyControls.Button {
                        text: qsTr("Delete Specific Fingerprint")
                        enabled: switchZa300FingerPrint.checked
                        onClicked: dialogDelZ.open()
                    }

                    MyControls.Button {
                        text: qsTr("Search Fingerprint")
                        enabled: switchZa300FingerPrint.checked
                        onClicked: za300FingerPrint.search_fingerprint()
                    }

                    MyControls.Button {
                        text: qsTr("Delete All Fingerprints")
                        enabled: switchZa300FingerPrint.checked
                        onClicked: za300FingerPrint.clean_flash()
                    }
                }
            }
        }
    }

    MyComponents.TerminalOutput {
        id: terminalOutputFp
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
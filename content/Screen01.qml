/*
This is a UI file (.ui.qml) that is intended to be edited in Qt Design Studio only.
It is supposed to be strictly declarative and only uses a subset of QML. If you edit
this file manually, you might introduce QML code that is not supported by Qt Design Studio.
Check out https://doc.qt.io/qtcreator/creator-quick-ui-forms.html for details on .ui.qml files.
*/

import QtQuick 6.5
import QtQuick.Controls 6.5
import QtQuick.Layouts 6.5
import QtMultimedia 6.5
import QtQuick.Dialogs 6.5

import MidToolUI
import Controls as MyControls

import src.process
import src.camera
import src.system
import src.fingerprint


Rectangle {
    id: rectangle1
    width: Constants.width
    height: Constants.height

    color: Constants.backgroundColor

    Rectangle {
        height: 60
        color: "#0066E0"
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.rightMargin: 0
        anchors.leftMargin: 0
        anchors.topMargin: 0

        Image {
            anchors.left: parent.left
            anchors.top: parent.top
            anchors.leftMargin: 20
            anchors.topMargin: 14
            source: "images/logo.png"
            fillMode: Image.PreserveAspectFit
        }
    }

    TabBar {
        id: tabBar
        height: 60
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.topMargin: 60
        currentIndex: swipeView.currentIndex

        // background: Rectangle {
        //     color: "#FFFFFF"
        //     radius: 8
        // }

        MyControls.TabButton {
            id: tabButtonMonitor
            text: qsTr("Monitoring")
        }

        MyControls.TabButton {
            id: tabButtonDeploy
            text: qsTr("Deployment")
        }

        MyControls.TabButton {
            id: tabButtonConfig
            text: qsTr("Configuration")
        }

        MyControls.TabButton {
            id: tabButtonSerial
            text: qsTr("Serial Port Data")
        }

        MyControls.TabButton {
            id: tabButtonFingerprint
            text: qsTr("Fingerprint Test")
        }

        MyControls.TabButton {
            id: tabButtonCamera
            text: qsTr("Camera Preview")
        }

        MyControls.TabButton {
            id: tabButtonFace
            text: qsTr("Face Recognition")
        }
    }

    SwipeView {
        id: swipeView
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        anchors.topMargin: 120
        // currentIndex: 0
        currentIndex: tabBar.currentIndex

        Rectangle {
            color: "transparent"

            MyControls.GroupBox {
                id: groupBox
                width: 400
                height: 160
                anchors.left: parent.left
                anchors.top: parent.top
                anchors.topMargin: 16
                anchors.leftMargin: 16

                Label {
                    text: qsTr("Middleware Service Management")
                    font.pixelSize: 16
                    font.bold: true
                }

                Process {
                    id: process
                    Component.onCompleted: process.Stdout.connect(textArea.append)
                }

                FileDialog {
                    id: fileDialog
                    title: qsTr("Please select middleware config file")
                    nameFilters: [qsTr("Json file (*.json)"), qsTr("Config file (*.conf)")]
                    onAccepted: process.start_middleware(selectedFile)
                    }

                RowLayout {
                    anchors.fill: parent
                    anchors.rightMargin: 20
                    anchors.leftMargin: 20
                    anchors.bottomMargin: 50
                    anchors.topMargin: 50

                    MyControls.Button {
                        id: buttonStart
                        text: qsTr("Start")
                        onClicked: fileDialog.open()
                    }

                    MyControls.Button {
                        id: buttonRestart
                        text: qsTr("Restart")
                        onClicked: process.restart_middleware()
                    }

                    MyControls.Button {
                        id: buttonStop
                        text: qsTr("Stop")
                        onClicked: {
                            process.stop_middleware()
                            // process.kill()
                        }
                    }
                }
            }

            MyControls.GroupBox {
                id: groupBox1
                height: 160
                anchors.left: groupBox.right
                anchors.right: parent.right
                anchors.top: parent.top
                anchors.leftMargin: 16
                anchors.topMargin: 16
                anchors.rightMargin: 16

                Label {
                    text: qsTr("Service Running Status")
                    font.pixelSize: 16
                    font.bold: true
                }

                Timer {
                    interval: 1000; running: true; repeat: true
                    onTriggered: listView.model.set_data()
                }

                ListView {
                    id: listView
                    anchors.fill: parent
                    anchors.bottomMargin: 50
                    anchors.topMargin: 50
                    anchors.rightMargin: 50
                    anchors.leftMargin: 50
                    orientation: ListView.Horizontal
                    model: SystemInfoModel {}
                    delegate: Item {
                        x: 5
                        width: 100
                        height: 40
                        Column {
                            Row {
                                Text {
                                    text: name
                                    font.bold: true
                                }
                                Text {
                                    text: percent + "%"
                                }
                                spacing: 2
                            }
                            MyControls.ProgressBar {
                                width: 90
                                value: percent / 100
                            }
                            spacing: 10
                        }
                    }
                }
            }

            MyControls.GroupBox {
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                anchors.leftMargin: 16
                anchors.rightMargin: 16
                anchors.topMargin: 192
                anchors.bottomMargin: 16

                Label {
                    text: qsTr("Terminal Output")
                    font.pixelSize: 16
                    font.bold: true
                }

                MyControls.Button {
                    anchors.right: parent.right
                    anchors.top: parent.top
                    text: qsTr("Clear")
                    onClicked: textArea.clear()
                }

                ScrollView {
                    anchors.left: parent.left
                    anchors.right: parent.right
                    anchors.top: parent.top
                    anchors.bottom: parent.bottom
                    anchors.topMargin: 54

                    background: Rectangle {
                        border.color: "#CAD0E0"
                        radius: 8
                    }

                    TextArea {
                        id: textArea
                        anchors.fill: parent
                        readOnly: true
                    }
                }
            }
        }

        Rectangle {
            color: "transparent"

            MyControls.VertTabBar {
                id: vertTabBarDeploy
                width: 180
                anchors.left: parent.left
                anchors.top: parent.top
                anchors.bottom: parent.bottom

                MyControls.TabButton {
                    anchors.left: parent.left
                    anchors.right: parent.right
                    text: qsTr("Deploy")
                }

                MyControls.TabButton {
                    anchors.left: parent.left
                    anchors.right: parent.right
                    text: qsTr("Update")
                }

                MyControls.TabButton {
                    anchors.left: parent.left
                    anchors.right: parent.right
                    text: qsTr("Backup")
                }

                MyControls.TabButton {
                    anchors.left: parent.left
                    anchors.right: parent.right
                    text: qsTr("Restore")
                }
            }

            StackLayout {
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.top: parent.top
                anchors.bottom: groupBoxDeploy.top
                anchors.leftMargin: 196
                anchors.rightMargin: 16
                anchors.topMargin: 16
                anchors.bottomMargin: 16
                currentIndex: vertTabBarDeploy.currentIndex

                MyControls.GroupBox {
                    height: 110
                    Layout.fillHeight: true
                    Layout.fillWidth: true

                    Label {
                        text: qsTr("Config")
                        font.pixelSize: 16
                        font.bold: true
                    }
                }

                MyControls.GroupBox {
                    height: 110
                    Layout.fillHeight: true
                    Layout.fillWidth: true

                    Label {
                        text: qsTr("Config")
                        font.pixelSize: 16
                        font.bold: true
                    }
                }

                MyControls.GroupBox {
                    height: 110
                    Layout.fillHeight: true
                    Layout.fillWidth: true

                    Label {
                        text: qsTr("Config")
                        font.pixelSize: 16
                        font.bold: true
                    }
                }

                MyControls.GroupBox {
                    height: 110
                    Layout.fillHeight: true
                    Layout.fillWidth: true

                    Label {
                        text: qsTr("Config")
                        font.pixelSize: 16
                        font.bold: true
                    }
                }
            }

            MyControls.GroupBox {
                id: groupBoxDeploy
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                anchors.bottomMargin: 16
                anchors.rightMargin: 16
                anchors.leftMargin: 196
                anchors.topMargin: 192


                Label {
                    text: qsTr("Terminal Output")
                    font.pixelSize: 16
                    font.bold: true
                }

                MyControls.Button {
                    anchors.right: parent.right
                    anchors.top: parent.top
                    text: qsTr("Clear")
                    onClicked: textAreaDeploy.clear()
                }

                ScrollView {
                    anchors.left: parent.left
                    anchors.right: parent.right
                    anchors.top: parent.top
                    anchors.bottom: parent.bottom
                    anchors.topMargin: 54

                    background: Rectangle {
                        border.color: "#CAD0E0"
                        radius: 8
                    }

                    TextArea {
                        id: textAreaDeploy
                        anchors.fill: parent
                        readOnly: true
                    }
                }
            }
        }

        Rectangle {
            color: "transparent"
        }

        Rectangle {
            color: "transparent"

            MyControls.GroupBox {
                id: groupBoxSerialConfig
                height: 110
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.top: parent.top
                anchors.rightMargin: 16
                anchors.leftMargin: 16
                anchors.topMargin: 16

                Label {
                    text: qsTr("Config")
                    font.pixelSize: 16
                    font.bold: true
                }

                GridLayout {
                    anchors.fill: parent
                    anchors.rightMargin: 300
                    anchors.bottomMargin: 20
                    anchors.topMargin: 20
                    anchors.leftMargin: 300
                    rows: 1
                    columns: 5

                    Label {
                        text: qsTr("Serial Port")
                        font.pixelSize: 16
                    }

                    MyControls.ComboBox {
                        model: squareFingerPrint.coms
                        // currentIndex: -1
                    }

                    Label {
                        text: qsTr("Baud Rate")
                        font.pixelSize: 16
                    }

                    MyControls.ComboBox {
                        model: squareFingerPrint.baud_rates
                    }

                    MyControls.Switch {
                        text: qsTr("Connect")
                        onCheckedChanged: {
                            if (checked) {
                                // let ret = squareFingerPrint.open_device(comboBoxComS.currentValue, comboBoxBaudRateS.currentValue)
                                console.log("library return:")
                            } else {
                                // let ret = squareFingerPrint.close_device()
                                console.log("library return:")
                            }
                        }
                    }
                }
            }

            MyControls.GroupBox {
                id: groupBox3
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.top: groupBoxSerialConfig.bottom
                anchors.bottom: parent.bottom
                anchors.leftMargin: 16
                anchors.rightMargin: 16
                anchors.topMargin: 16
                anchors.bottomMargin: 16

                Label {
                    text: qsTr("Terminal Output")
                    font.pixelSize: 16
                    font.bold: true
                }

                MyControls.Button {
                    anchors.right: parent.right
                    anchors.top: parent.top
                    text: qsTr("Clear")
                    onClicked: textAreaSerial.clear()
                }

                ScrollView {
                    anchors.left: parent.left
                    anchors.right: parent.right
                    anchors.top: parent.top
                    anchors.bottom: parent.bottom
                    anchors.topMargin: 54

                    background: Rectangle {
                        border.color: "#CAD0E0"
                        radius: 8
                    }

                    TextArea {
                        id: textAreaSerial
                        anchors.fill: parent
                        readOnly: true
                    }
                }
            }
        }

        Rectangle {
            color: "transparent"

            MyControls.VertTabBar {
                id: vertTabBarFingerprint
                width: 180
                anchors.left: parent.left
                anchors.top: parent.top
                anchors.bottom: parent.bottom

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
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.top: parent.top
                anchors.bottom: groupBoxFPOutput.top
                anchors.rightMargin: 16
                anchors.leftMargin: 196
                anchors.bottomMargin: 16
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
                        width: 500
                        height: 160
                        anchors.left: parent.left
                        anchors.top: parent.top
                        anchors.bottom: parent.bottom

                        Label {
                            text: qsTr("Config")
                            font.pixelSize: 16
                            font.bold: true
                        }

                        GridLayout {
                            anchors.fill: parent
                            anchors.bottomMargin: 20
                            anchors.topMargin: 20
                            anchors.leftMargin: 50
                            rows: 2
                            columns: 3

                            Label {
                                text: qsTr("Serial Port")
                                font.pixelSize: 16
                            }

                            MyControls.ComboBox {
                                id: comboBoxComS
                                model: squareFingerPrint.coms
                                // currentIndex: -1
                            }

                            MyControls.Switch {
                                text: qsTr("Connect")
                                onCheckedChanged: {
                                    if (checked) {
                                        let ret = squareFingerPrint.open_device(comboBoxComS.currentValue, comboBoxBaudRateS.currentValue)
                                        console.log("library return:", ret)
                                    } else {
                                        let ret = squareFingerPrint.close_device()
                                        console.log("library return:", ret)
                                    }
                                }
                            }

                            Label {
                                text: qsTr("Baud Rate")
                                font.pixelSize: 16
                            }

                            MyControls.ComboBox {
                                id: comboBoxBaudRateS
                                model: squareFingerPrint.baud_rates
                                // currentIndex: -1
                            }
                        }
                    }

                    MyControls.GroupBox {
                        height: 160
                        anchors.left: groupBoxConfigS.right
                        anchors.right: parent.right
                        anchors.top: parent.top
                        anchors.bottom: parent.bottom
                        anchors.leftMargin: 16

                        Label {
                            text: qsTr("Function")
                            font.pixelSize: 16
                            font.bold: true
                        }

                        GridLayout {
                            anchors.fill: parent
                            anchors.leftMargin: 100
                            rows: 3
                            columns: 2

                            Dialog {
                                id: dialogSet
                                modal: true
                                title: "Please input an integer from 1 to 1049."
                                standardButtons: Dialog.Ok | Dialog.Cancel
                                onAccepted: {
                                    if (textFieldSetID.text) {
                                        squareFingerPrint.get_fingerprint(textFieldSetID.text)
                                    }
                                }

                                contentItem: Rectangle {
                                    color: "#FFFFFF"
                                    implicitWidth: 200
                                    implicitHeight: 50

                                    TextField {
                                        id: textFieldSetID
                                        anchors.centerIn: parent
                                        placeholderText: qsTr("Input an integer")
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
                                title: "Please input an integer from 1 to 1049."
                                standardButtons: Dialog.Ok | Dialog.Cancel
                                onAccepted: {
                                    if (textFieldDelIDS.text) {
                                        squareFingerPrint.del_flash(textFieldDelIDS.text)
                                    }
                                }

                                contentItem: Rectangle {
                                    color: "#FFFFFF"
                                    implicitWidth: 200
                                    implicitHeight: 50

                                    TextField {
                                        id: textFieldDelIDS
                                        anchors.centerIn: parent
                                        placeholderText: qsTr("Input an integer")
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
                        width: 500
                        height: 160
                        anchors.left: parent.left
                        anchors.top: parent.top
                        anchors.bottom: parent.bottom

                        Label {
                            text: qsTr("Config")
                            font.pixelSize: 16
                            font.bold: true
                        }

                        GridLayout {
                            anchors.fill: parent
                            anchors.bottomMargin: 20
                            anchors.topMargin: 20
                            anchors.leftMargin: 50
                            rows: 2
                            columns: 3

                            Label {
                                text: qsTr("Serial Port")
                                font.pixelSize: 16
                            }

                            MyControls.ComboBox {
                                id: comboBoxComR
                                model: roundFingerPrint.coms
                                // currentIndex: -1
                                textRole: "text"
                                valueRole: "value"
                            }

                            MyControls.Switch {
                                text: qsTr("Connect")
                                onCheckedChanged: {
                                    if (checked) {
                                        let ret = roundFingerPrint.open_device(comboBoxComR.currentValue, comboBoxBaudRateR.currentValue)
                                        console.log("library return:", ret)
                                    } else {
                                        let ret = roundFingerPrint.close_device()
                                        console.log("library return:", ret)
                                    }
                                }
                            }

                            Label {
                                text: qsTr("Baud Rate")
                                font.pixelSize: 16
                            }

                            MyControls.ComboBox {
                                id: comboBoxBaudRateR
                                model: roundFingerPrint.baud_rates
                                // currentIndex: -1
                            }
                        }
                    }

                    MyControls.GroupBox {
                        height: 160
                        anchors.left: groupBoxConfigR.right
                        anchors.right: parent.right
                        anchors.top: parent.top
                        anchors.bottom: parent.bottom
                        anchors.leftMargin: 16

                        Label {
                            text: qsTr("Function")
                            font.pixelSize: 16
                            font.bold: true
                        }

                        GridLayout {
                            anchors.fill: parent
                            anchors.leftMargin: 100
                            rows: 2
                            columns: 2

                            MyControls.Button {
                                text: qsTr("Collect Fingerprint")
                                onClicked: roundFingerPrint.get_fingerprint()
                            }

                            Dialog {
                                id: dialogDelR
                                modal: true
                                title: "Please input an integer from 1 to 500."
                                standardButtons: Dialog.Ok | Dialog.Cancel
                                onAccepted: {
                                    if (textFieldDelIDR.text) {
                                        roundFingerPrint.del_flash(textFieldDelIDR.text)
                                    }
                                }

                                contentItem: Rectangle {
                                    color: "#FFFFFF"
                                    implicitWidth: 200
                                    implicitHeight: 50

                                    TextField {
                                        id: textFieldDelIDR
                                        anchors.centerIn: parent
                                        placeholderText: qsTr("Input an integer")
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
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                anchors.bottomMargin: 16
                anchors.rightMargin: 16
                anchors.leftMargin: 196
                anchors.topMargin: 192


                Label {
                    text: qsTr("Terminal Output")
                    font.pixelSize: 16
                    font.bold: true
                }

                MyControls.Button {
                    anchors.right: parent.right
                    anchors.top: parent.top
                    text: qsTr("Clear")
                    onClicked: textAreaFingerprint.clear()
                }

                ScrollView {
                    anchors.left: parent.left
                    anchors.right: parent.right
                    anchors.top: parent.top
                    anchors.bottom: parent.bottom
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

        Rectangle {
            color: "transparent"

            Rectangle {
                color: "#FFFFFF"
                radius: 8
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                anchors.rightMargin: 16
                anchors.leftMargin: 16
                anchors.bottomMargin: 16
                anchors.topMargin: 16

                CameraModel {
                    id: cameraModel
                }

                CaptureSession {
                    id: cptureSession
                    camera: Camera {
                        cameraDevice: comboBox.currentValue
                    }
                    videoOutput: videoOutput
                }

                Rectangle {
                    color: "#ECF0F5"
                    radius: 8
                    x: 550
                    width: 664
                    height: 384
                    anchors.verticalCenter: parent.verticalCenter
                    VideoOutput {
                        id: videoOutput
                        anchors.fill: parent
                        anchors.rightMargin: 12
                        anchors.leftMargin: 12
                        anchors.bottomMargin: 12
                        anchors.topMargin: 12
                    }
                }

                RowLayout {
                    x: 38
                    y: 92
                    width: 480
                    height: 40

                    Label {
                        text: qsTr("Camera")
                        font.pixelSize: 16
                    }

                    MyControls.ComboBox {
                        id: comboBox
                        Layout.preferredWidth: 219
                        Layout.preferredHeight: 40
                        model: cameraModel.cameras
                        // currentIndex: -1
                        textRole: "text"
                        valueRole: "value"
                    }

                    MyControls.Switch {
                        id: switch1
                        text: qsTr("Open Camera")
                        onCheckedChanged: {
                            if (checked) {
                                cptureSession.camera.start()
                            } else {
                                cptureSession.camera.stop()
                            }
                        }
                    }
                }
            }
        }

        Rectangle {
            color: "transparent"
        }

        Rectangle {
            color: "transparent"
        }
    }
}

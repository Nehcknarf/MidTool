import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import Controls as MyControls


Rectangle {
    color: "#D9DDE9"
    height: 720
    width: 1280

    function funcVisible() {
        switch (Qt.platform.os) {
            case "windows":
                return false
            case "linux":
                return true
        }
    }

    function maintenanceTip() {
        labelDrawer.text = qsTr("* Please do not execute any operation which might cause corruption of middleware files.")
        drawer.open()
        timer.running = true
    }

    function fingerprintTip() {
        labelDrawer.text = qsTr("* Please stop middleware service first before testing fingerprint sensor.")
        drawer.open()
        timer.running = true
    }

    function faceRecognitionTip() {
        labelDrawer.text = qsTr("* Please check if you can connect to the Internet first.")
        drawer.open()
        timer.running = true
    }

    Drawer {
        id: drawer
        height: 60
        width: mainScreen.width
        closePolicy: Popup.CloseOnPressOutside
        edge: Qt.TopEdge
        dragMargin: 0
        modal: false

        background: Rectangle {
            color: "#FDF4F5"
            height: parent.height
            width: parent.width
        }

        Label {
            id: labelDrawer
            font.family: medium.name
            font.pixelSize: 16
            anchors.centerIn: parent
        }

        Timer {
            id: timer
            interval: 3000
            repeat: false
            running: false
            onTriggered: drawer.close()
        }
    }

    Rectangle {
        height: 60
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        color: "#0066E0"

        MouseArea {
            anchors.fill: parent

            property var pressedPos: "0,0"

            onClicked: {
                Qt.inputMethod.hide()
            }

            onPressed: mouse => {
                pressedPos = Qt.point(mouse.x, mouse.y)
            }

            onPositionChanged: mouse => {
                let delta = Qt.point(mouse.x - pressedPos.x, mouse.y - pressedPos.y)
                window.x += delta.x
                window.y += delta.y
            }
        }

        Image {
            anchors.left: parent.left
            anchors.leftMargin: 20
            anchors.top: parent.top
            anchors.topMargin: 14
            fillMode: Image.PreserveAspectFit
            source: "qrc:/content/images/logo.png"
        }

        Popup {
            id: popupAbout
            x: (window.width - width) / 2
            y: (window.height - height) / 2
            modal: true

            background: Rectangle {
                // border.color: "#FFFFFF"
                radius: 8
            }

            ColumnLayout {
                RowLayout {
                    Layout.alignment: Qt.AlignHCenter
                    Label {
                        text: qsTr("About")
                        font.family: bold.name
                        font.pixelSize: 20
                    }
                }

                RowLayout {
                    Layout.alignment: Qt.AlignHCenter
                    Image {
                        Layout.preferredHeight: 64
                        Layout.preferredWidth: 64
                        fillMode: Image.PreserveAspectFit
                        source: "qrc:/content/images/icon.png"
                    }

                    Label {
                        text: "MidTool " + midToolVersion
                        font.family: medium.name
                        font.pixelSize: 16
                    }
                }

                RowLayout {
                    Layout.alignment: Qt.AlignHCenter
                    Label {
                        text: qsTr("Build on ") + buildDate
                        font.family: medium.name
                        font.pixelSize: 16
                    }
                }

                RowLayout {
                    Layout.alignment: Qt.AlignHCenter
                    Label {
                        text: qsTr("Powered by") + " Python " + pythonVersion + " & Qt " + qtVersion
                        font.family: medium.name
                        font.pixelSize: 16
                    }
                }

                RowLayout {
                    Layout.alignment: Qt.AlignHCenter
                    Label {
                        text: qsTr("Copyright @ 2022-2023 NuboMed. All Rights Reserved.")
                        font.family: medium.name
                        font.pixelSize: 16
                    }
                }
            }
        }

        Image {
            height: 32
            width: 32
            anchors.right: parent.right
            anchors.rightMargin: 66
            anchors.top: parent.top
            anchors.topMargin: 14
            fillMode: Image.PreserveAspectFit
            source: "qrc:/content/images/about.svg"

            MouseArea {
                anchors.fill: parent
                onClicked: popupAbout.open()
            }
        }

        Image {
            height: 32
            width: 32
            anchors.right: parent.right
            anchors.rightMargin: 20
            anchors.top: parent.top
            anchors.topMargin: 14
            fillMode: Image.PreserveAspectFit
            source: "qrc:/content/images/close.svg"

            MouseArea {
                anchors.fill: parent
                onClicked: Qt.quit()
            }
        }
    }

    TabBar {
        id: tabBar
        height: 60
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.topMargin: 60
        currentIndex: argCurrentIndex != null ? argCurrentIndex : swipeView.currentIndex

        // background: Rectangle {
        //     color: "#FFFFFF"
        //     radius: 8
        // }

        MyControls.TabButton {
            text: qsTr("Monitoring")
            visible: argCurrentIndex === 0 || argCurrentIndex == null
        }

        MyControls.TabButton {
            text: qsTr("Maintenance")
            visible: argCurrentIndex === 1 || argCurrentIndex == null
            onClicked: maintenanceTip()
        }

        MyControls.TabButton {
            text: qsTr("Config Editor")
            visible: argCurrentIndex === 2 || argCurrentIndex == null
        }

        MyControls.TabButton {
            text: qsTr("Serial Port")
            visible: argCurrentIndex === 3 || argCurrentIndex == null
        }

        MyControls.TabButton {
            text: qsTr("Fingerprint")
            visible: argCurrentIndex === 4 || argCurrentIndex == null
            onClicked: fingerprintTip()
        }

        MyControls.TabButton {
            text: qsTr("RFID Reader")
            visible: argCurrentIndex === 5 || argCurrentIndex == null
        }

        MyControls.TabButton {
            text: qsTr("Face Recognition")
            visible: argCurrentIndex === 6 || argCurrentIndex == null
            onClicked: faceRecognitionTip()
        }

        MyControls.TabButton {
            text: qsTr("Camera")
            visible: argCurrentIndex === 7 || argCurrentIndex == null
        }

        MyControls.TabButton {
            text: qsTr("Network")
            visible: argCurrentIndex === 8 || argCurrentIndex == null
        }

        MyControls.TabButton {
            text: qsTr("Time")
            visible: argCurrentIndex === 9 || argCurrentIndex == null
        }

        MyControls.TabButton {
            text: qsTr("Log Downloader")
            visible: argCurrentIndex === 10 || argCurrentIndex == null
        }
    }

    SwipeView {
        id: swipeView
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.topMargin: 120
        currentIndex: tabBar.currentIndex
        interactive: argCurrentIndex == null

        onCurrentIndexChanged: {
            switch (currentIndex) {
                case 1:
                    maintenanceTip()
                    break
                case 4:
                    fingerprintTip()
                    break
                case 6:
                    faceRecognitionTip()
                    break
            }
        }

        Loader {
            source: "qrc:/content/Monitoring.qml"
            // active: SwipeView.isCurrentItem || SwipeView.isNextItem || SwipeView.isPreviousItem
        }

        Loader {
            source: "qrc:/content/Maintenance.qml"
            // active: SwipeView.isCurrentItem || SwipeView.isNextItem || SwipeView.isPreviousItem
        }

        Loader {
            source: {
                switch (productType) {
                    // 耗材柜
                    case 0:
                        return "qrc:/content/EditorConsumable.qml"
                    // 药品柜
                    case 1:
                        return "qrc:/content/EditorDrug.qml"
                    // 抢救车 抢救车还未规划配置项，展示空页
                    case 2:
                        return "qrc:/content/EditorEcart.qml"
                    // 未知设备 默认展示耗材柜设置页
                    case -1:
                        return "qrc:/content/EditorConsumable.qml"
                }
            }
            // active: SwipeView.isCurrentItem || SwipeView.isNextItem || SwipeView.isPreviousItem
        }

        Loader {
            source: "qrc:/content/Serial.qml"
            // active: SwipeView.isCurrentItem || SwipeView.isNextItem || SwipeView.isPreviousItem
        }

        Loader {
            source: "qrc:/content/Fingerprint.qml"
            // active: SwipeView.isCurrentItem || SwipeView.isNextItem || SwipeView.isPreviousItem
        }

        Loader {
            source: "qrc:/content/Reader.qml"
            // active: SwipeView.isCurrentItem || SwipeView.isNextItem || SwipeView.isPreviousItem
        }

        Loader {
            source: "qrc:/content/Activation.qml"
            // active: SwipeView.isCurrentItem || SwipeView.isNextItem || SwipeView.isPreviousItem
        }

        Loader {
            source: "qrc:/content/Camera.qml"
            // active: SwipeView.isCurrentItem || SwipeView.isNextItem || SwipeView.isPreviousItem
        }

        Loader {
            source: "qrc:/content/Network.qml"
            // active: SwipeView.isCurrentItem || SwipeView.isNextItem || SwipeView.isPreviousItem
        }

        Loader {
            source: "qrc:/content/Timezone.qml"
            // active: funcVisible()
            // active: SwipeView.isCurrentItem || SwipeView.isNextItem || SwipeView.isPreviousItem
        }

        Loader {
            source: "qrc:/content/LogDownloader.qml"
            // active: SwipeView.isCurrentItem || SwipeView.isNextItem || SwipeView.isPreviousItem
        }
    }
}

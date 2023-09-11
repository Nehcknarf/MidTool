import QtQuick 6.5
import QtQuick.Controls 6.5

import Controls as MyControls


Rectangle {
    color: "#D9DDE9"
    height: 720
    width: 1280

    // property string system
    // property int productType

    Drawer {
        id: drawer
        closePolicy: Popup.CloseOnPressOutside
        dragMargin: 0
        edge: Qt.TopEdge
        height: 60
        modal: false
        width: 1280

        background: Rectangle {
            Rectangle {
                color: "#FDF4F5"
                height: parent.height
                width: 1280
            }
        }

        Label {
            id: labelDrawer
            font.family: medium.font.family
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
        anchors.left: parent.left
        anchors.leftMargin: 0
        anchors.right: parent.right
        anchors.rightMargin: 0
        anchors.top: parent.top
        anchors.topMargin: 0
        color: "#0066E0"
        height: 60

        MouseArea {
            id: mouseArea
            anchors.fill: parent
            onClicked: Qt.inputMethod.hide()
        }

        Image {
            anchors.left: parent.left
            anchors.leftMargin: 20
            anchors.top: parent.top
            anchors.topMargin: 14
            fillMode: Image.PreserveAspectFit
            source: "qrc:/content/images/logo.png"
        }

        Image {
            anchors.right: parent.right
            anchors.rightMargin: 20
            anchors.top: parent.top
            anchors.topMargin: 20
            fillMode: Image.PreserveAspectFit
            height: 20
            width: 20
            source: "qrc:/content/images/close.svg"
            MouseArea {
                anchors.fill: parent
                onClicked: Qt.quit()
            }
        }
    }

    TabBar {
        id: tabBar

        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.topMargin: 60
        currentIndex: argCurrentIndex != null ? argCurrentIndex : swipeView.currentIndex
        height: 60

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

            onClicked: {
                labelDrawer.text = qsTr("* Please do not execute any operation which might cause corruption of middleware files.")
                drawer.open()
                timer.running = true
            }
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
        }

        MyControls.TabButton {
            text: qsTr("Face Recognition")
            visible: argCurrentIndex === 5 || argCurrentIndex == null

            onClicked: {
                labelDrawer.text = qsTr("* Please check if you can connect to the Internet first.")
                drawer.open()
                timer.running = true
            }
        }

        MyControls.TabButton {
            text: qsTr("Camera")
            visible: argCurrentIndex === 6 || argCurrentIndex == null
        }

        MyControls.TabButton {
            text: qsTr("Network")
            visible: argCurrentIndex === 7 || argCurrentIndex == null
        }

        MyControls.TabButton {
            text: qsTr("Time")
            visible: argCurrentIndex === 8 || argCurrentIndex == null
        }

        MyControls.TabButton {
            text: qsTr("Log Downloader")
            visible: argCurrentIndex === 9 || argCurrentIndex == null
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

        Item {
            Loader {
                anchors.fill: parent
                source: "qrc:/content/Monitoring.qml"
                // active: SwipeView.isCurrentItem || SwipeView.isNextItem || SwipeView.isPreviousItem
            }
        }
        Item {
            Loader {
                anchors.fill: parent
                source: "qrc:/content/Maintenance.qml"
                // active: SwipeView.isCurrentItem || SwipeView.isNextItem || SwipeView.isPreviousItem
            }
        }
        Item {
            Loader {
                anchors.fill: parent
                source: "qrc:/content/EditorDrug.qml"
                // active: SwipeView.isCurrentItem || SwipeView.isNextItem || SwipeView.isPreviousItem
            }
        }
        Item {
           Loader {
                anchors.fill: parent
                source: "qrc:/content/Serial.qml"
                // active: SwipeView.isCurrentItem || SwipeView.isNextItem || SwipeView.isPreviousItem
            }
        }
        Item {
           Loader {
                anchors.fill: parent
                source: "qrc:/content/Fingerprint.qml"
                // active: SwipeView.isCurrentItem || SwipeView.isNextItem || SwipeView.isPreviousItem
            }
        }
        Item {
           Loader {
                anchors.fill: parent
                source: "qrc:/content/Activation.qml"
                // active: SwipeView.isCurrentItem || SwipeView.isNextItem || SwipeView.isPreviousItem
            }
        }
        Item {
           Loader {
                anchors.fill: parent
                source: "qrc:/content/Camera.qml"
                // active: SwipeView.isCurrentItem || SwipeView.isNextItem || SwipeView.isPreviousItem
            }
        }
        Item {
           Loader {
                anchors.fill: parent
                source: "qrc:/content/Network.qml"
                // active: SwipeView.isCurrentItem || SwipeView.isNextItem || SwipeView.isPreviousItem
            }
        }
        Item {
           Loader {
                anchors.fill: parent
                source: "qrc:/content/Timezone.qml"
                // active: SwipeView.isCurrentItem || SwipeView.isNextItem || SwipeView.isPreviousItem
            }
        }
        Item {
           Loader {
                anchors.fill: parent
                source: "qrc:/content/LogDownloader.qml"
                // active: SwipeView.isCurrentItem || SwipeView.isNextItem || SwipeView.isPreviousItem
            }
        }
    }
}

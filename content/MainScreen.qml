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
        currentIndex: swipeView.currentIndex
        height: 60

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

            text: qsTr("Maintenance")

            onClicked: {
                labelDrawer.text = qsTr("* Please do not execute any operation which might cause corruption of middleware files.")
                drawer.open()
                timer.running = true
            }
        }
        MyControls.TabButton {
            id: tabButtonConfig

            text: qsTr("Config Editor")
        }
        MyControls.TabButton {
            id: tabButtonSerial

            text: qsTr("Serial Port")
        }
        MyControls.TabButton {
            id: tabButtonFingerprint

            text: qsTr("Fingerprint")
        }
        MyControls.TabButton {
            id: tabButtonFace

            text: qsTr("Face Recognition")

            onClicked: {
                labelDrawer.text = qsTr("* Please check if you can connect to the Internet first.")
                drawer.open()
                timer.running = true
            }
        }
        MyControls.TabButton {
            id: tabButtonCamera

            text: qsTr("Camera")
        }
        MyControls.TabButton {
            id: tabButtonNetwork

            text: qsTr("Network")
        }
        MyControls.TabButton {
            id: tabButtonTime

            text: qsTr("Time")
            // visible: false
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
                source: "qrc:/content/Time.qml"
                // active: SwipeView.isCurrentItem || SwipeView.isNextItem || SwipeView.isPreviousItem
            }
        }
    }
}

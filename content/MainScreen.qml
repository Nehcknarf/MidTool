/*
This is a UI file (.ui.qml) that is intended to be edited in Qt Design Studio only.
It is supposed to be strictly declarative and only uses a subset of QML. If you edit
this file manually, you might introduce QML code that is not supported by Qt Design Studio.
Check out https://doc.qt.io/qtcreator/creator-quick-ui-forms.html for details on .ui.qml files.
*/

import QtQuick 6.5
import QtQuick.Controls 6.5

import MidToolUI
import Controls as MyControls


Rectangle {
    color: Constants.backgroundColor
    height: Constants.height
    width: Constants.width

    Drawer {
        id: drawer

        closePolicy: Popup.CloseOnPressOutside
        dragMargin: 0
        edge: Qt.TopEdge
        height: 60
        modal: false
        width: Constants.width

        background: Rectangle {
            Rectangle {
                color: "#FDF4F5"
                height: parent.height
                width: Constants.width
            }
        }

        Label {
            anchors.centerIn: parent
            text: "Please check if you can connect to the Internet."
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

        Image {
            anchors.left: parent.left
            anchors.leftMargin: 20
            anchors.top: parent.top
            anchors.topMargin: 14
            fillMode: Image.PreserveAspectFit
            source: "images/logo.png"
        }

        Image {
            anchors.right: parent.right
            anchors.rightMargin: 20
            anchors.top: parent.top
            anchors.topMargin: 20
            fillMode: Image.PreserveAspectFit
            height: 20
            width: 20
            source: "images/close.svg"
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

            onClicked: drawer.open()
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
                source: "Monitoring.qml"
                // active: SwipeView.isCurrentItem || SwipeView.isNextItem || SwipeView.isPreviousItem
            }
        }
        Item {
            Loader {
                anchors.fill: parent
                source: "Maintenance.qml"
                // active: SwipeView.isCurrentItem || SwipeView.isNextItem || SwipeView.isPreviousItem
            }
        }
        Item {
            Loader {
                anchors.fill: parent
                source: "EditorDrug.qml"
                // active: SwipeView.isCurrentItem || SwipeView.isNextItem || SwipeView.isPreviousItem
            }
        }
        Item {
           Loader {
                anchors.fill: parent
                source: "Serial.qml"
                // active: SwipeView.isCurrentItem || SwipeView.isNextItem || SwipeView.isPreviousItem
            }
        }
        Item {
           Loader {
                anchors.fill: parent
                source: "Fingerprint.qml"
                // active: SwipeView.isCurrentItem || SwipeView.isNextItem || SwipeView.isPreviousItem
            }
        }
        Item {
           Loader {
                anchors.fill: parent
                source: "Camera.qml"
                // active: SwipeView.isCurrentItem || SwipeView.isNextItem || SwipeView.isPreviousItem
            }
        }
        Item {
           Loader {
                anchors.fill: parent
                source: "Activation.qml"
                // active: SwipeView.isCurrentItem || SwipeView.isNextItem || SwipeView.isPreviousItem
            }
        }
    }
}

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
import MidToolUI
import Controls as MyControls

Rectangle {
    id: rectangle1
    width: Constants.width
    height: Constants.height

    color: Constants.backgroundColor

    Rectangle {
        id: rectangle
        height: 60
        color: "#0066E0"
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.rightMargin: 0
        anchors.leftMargin: 0
        anchors.topMargin: 0

        Image {
            id: image
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
        anchors.rightMargin: 0
        anchors.leftMargin: 0
        anchors.topMargin: 60
        currentIndex: swipeView.currentIndex
        // background: Rectangle {
        //     color: "#FFFFFF"
        //     radius: 8
        // }

        MyControls.TabButton {
            id: tabButtonCamera
            text: qsTr("Camera")
        }

        MyControls.TabButton {
            id: tabButtonSystem
            text: qsTr("System")
        }

        MyControls.TabButton {
            id: tabButtonSerial
            text: qsTr("Serial")
        }
    }

    SwipeView {
        id: swipeView
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        anchors.topMargin: 120
//        currentIndex: 0
        currentIndex: tabBar.currentIndex

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
                        anchors.left: parent.left
                        anchors.right: parent.right
                        anchors.top: parent.top
                        anchors.bottom: parent.bottom
                        anchors.rightMargin: 12
                        anchors.leftMargin: 12
                        anchors.bottomMargin: 12
                        anchors.topMargin: 12
                    }
                }

                RowLayout {
                    x: 20
                    y: 92
                    Text {
                        id: text1
                        text: qsTr("Camera:")
                        font.pixelSize: 16
                        opacity: 0.5
                        color: "#181D41"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                        Layout.preferredWidth: 101
                        Layout.preferredHeight: 40
                    }

                    MyControls.ComboBox {
                        id: comboBox
                        Layout.preferredWidth: 219
                        Layout.preferredHeight: 40
                        model: cameraListModel
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

                MyControls.Button {
                    id: button1
                    text: qsTr("获取可用串口")
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
            }
        }
    }
}

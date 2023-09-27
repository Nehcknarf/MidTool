import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtMultimedia

import Controls as MyControls

import src.camera


Item {
    MyControls.GroupBox {
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 16
        anchors.left: parent.left
        anchors.leftMargin: 16
        anchors.right: parent.right
        anchors.rightMargin: 16
        anchors.top: parent.top
        anchors.topMargin: 16

        Label {
            font.family: bold.font.family
            font.pixelSize: 16
            text: qsTr("Camera Preview")
        }

        CameraModel {
            id: cameraModel
        }

        MediaDevices {
            id: mediaDevices
        }

        CaptureSession {
            id: cptureSession
            videoOutput: videoOutput
            camera: Camera {
                cameraDevice: comboBoxCamera.currentValue === undefined ? mediaDevices.defaultVideoInput : comboBoxCamera.currentValue
            }
        }

        RowLayout {
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.verticalCenter: parent.verticalCenter

            Label {
                font.family: bold.font.family
                font.pixelSize: 16
                text: qsTr("Camera")
            }

            MyControls.ComboBox {
                id: comboBoxCamera
                model: cameraModel.cameras
                // currentIndex: -1
                textRole: "text"
                valueRole: "value"
            }

            Label {
                font.family: bold.font.family
                font.pixelSize: 16
                text: qsTr("Switch")
            }

            MyControls.Switch {
                onCheckedChanged: checked ? cptureSession.camera.start() : cptureSession.camera.stop()
            }

            Rectangle {
                color: "#ECF0F5"
                height: 384
                width: 664
                radius: 8

                VideoOutput {
                    id: videoOutput
                    anchors.bottomMargin: 12
                    anchors.fill: parent
                    anchors.leftMargin: 12
                    anchors.rightMargin: 12
                    anchors.topMargin: 12
                }
            }
        }
    }
}

import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtMultimedia

import Controls as MyControls

import src.camera


MyControls.GroupBox {
    anchors.fill: parent
    anchors.margins: 16

    Label {
        font.family: bold.name
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
        id: captureSession
        videoOutput: videoOutput
        camera: Camera {
            active: switchCamera.checked ? 1 : 0
            focusMode: Camera.FocusModeAutoNear
            cameraDevice: comboBoxCamera.currentValue === undefined ? mediaDevices.defaultVideoInput : comboBoxCamera.currentValue
            onErrorOccurred: function (error, errorString) {
                console.log(errorString)
            }
        }
    }

    RowLayout {
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenter: parent.verticalCenter

        Label {
            font.family: bold.name
            font.pixelSize: 16
            text: qsTr("Camera")
        }

        MyControls.ComboBox {
            id: comboBoxCamera
            model: cameraModel.cameras
            enabled: ! switchCamera.checked
            // currentIndex: -1
            textRole: "text"
            valueRole: "value"
        }

        Label {
            font.family: bold.name
            font.pixelSize: 16
            text: qsTr("Switch")
        }

        MyControls.Switch {
            id: switchCamera
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

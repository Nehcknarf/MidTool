import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtMultimedia

import Controls as MyControls


MyControls.GroupBox {
    anchors.fill: parent
    anchors.margins: 16

    Label {
        font.family: bold.font.family
        font.pixelSize: 16
        text: qsTr("Camera Preview")
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
            onErrorOccurred: function (error, errorString) {
                console.log(errorString)
            }
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
            model: mediaDevices.videoInputs
            textRole: "description"
            displayText: captureSession.camera.cameraDevice.description
            onActivated: captureSession.camera.cameraDevice = comboBoxCamera.currentValue
        }

        Label {
            font.family: bold.font.family
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

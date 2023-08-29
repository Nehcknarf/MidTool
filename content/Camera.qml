import QtQuick 6.5
import QtQuick.Controls 6.5
import QtMultimedia 6.5

import Controls as MyControls

import src.camera


Rectangle {
    anchors.bottom: parent.bottom
    anchors.bottomMargin: 16
    anchors.left: parent.left
    anchors.leftMargin: 16
    anchors.right: parent.right
    anchors.rightMargin: 16
    anchors.top: parent.top
    anchors.topMargin: 16
    color: "#FFFFFF"
    radius: 8

    CameraModel {
        id: cameraModel

    }
    CaptureSession {
        id: cptureSession

        videoOutput: videoOutput

        camera: Camera {
            cameraDevice: comboBoxCamera.currentValue
        }
    }
    Rectangle {
        anchors.verticalCenter: parent.verticalCenter
        color: "#ECF0F5"
        height: 384
        radius: 8
        width: 664
        x: 550

        VideoOutput {
            id: videoOutput

            anchors.bottomMargin: 12
            anchors.fill: parent
            anchors.leftMargin: 12
            anchors.rightMargin: 12
            anchors.topMargin: 12
        }
    }
    RowLayout {
        height: 40
        width: 480
        x: 38
        y: 92

        Label {
            font.pixelSize: 16
            text: qsTr("Camera")
        }
        MyControls.ComboBox {
            id: comboBoxCamera

            Layout.preferredHeight: 40
            Layout.preferredWidth: 219
            model: cameraModel.cameras
            // currentIndex: -1
            textRole: "text"
            valueRole: "value"
        }
        Label {
            font.pixelSize: 16
            text: qsTr("Switch")
        }
        MyControls.Switch {
            onCheckedChanged: checked ? cptureSession.camera.start() : cptureSession.camera.stop()
        }
    }
}
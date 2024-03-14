import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import Controls as MyControls


RowLayout {
    id: root

    property string cabinetId
    property string host
    property string antennaNo

    Label {
        font.family: bold.name
        font.pixelSize: 16
        text: qsTr("Cabinet ID")
    }

    MyControls.TextField {
        implicitWidth: 100
        text: root.cabinetId
        onTextChanged: {
            root.cabinetId = this.text
        }
    }

    Label {
        font.family: bold.name
        font.pixelSize: 16
        text: qsTr("Host")
    }

    MyControls.TextField {
        implicitWidth: 150
        text: root.host
        inputMethodHints: Qt.ImhDigitsOnly
        validator: RegularExpressionValidator {
            regularExpression: /((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})(\.((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})){3}/
        }
        onTextChanged: {
            root.host = this.text
        }
    }

    Label {
        font.family: bold.name
        font.pixelSize: 16
        text: qsTr("Antenna No. List")
    }

    MyControls.TextField {
        implicitWidth: 200
        text: root.antennaNo
        inputMethodHints: Qt.ImhPreferNumbers
        onTextChanged: {
            root.antennaNo = this.text
        }
    }

    MyControls.Button {
        implicitWidth: 40
        text: qsTr("-")
        onClicked: {
            parent.destroy()
        }
    }
}

import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import Controls as MyControls


RowLayout {
    id: root

    property string productNo
    property int channel

    Label {
        font.family: bold.name
        font.pixelSize: 16
        text: qsTr("Product No")
    }

    MyControls.TextField {
        implicitWidth: 100
        text: root.productNo
        onTextChanged: {
            root.productNo = this.text
        }
    }

    Label {
        font.family: bold.name
        font.pixelSize: 16
        text: qsTr("Channel")
    }

    MyControls.TextField {
        implicitWidth: 50
        text: root.channel
        inputMethodHints: Qt.ImhDigitsOnly
        onTextChanged: {
            root.channel = this.text
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

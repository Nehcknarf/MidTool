import QtQuick 6.5
import QtQuick.Controls 6.5

import Controls as MyControls


RowLayout {
    property string productNo
    property int channel

    Label {
        font.pixelSize: 16
        text: qsTr("Product No")
    }

    MyControls.TextField {
        implicitWidth: 100
        text: productNo
    }

    Label {
        font.pixelSize: 16
        text: qsTr("Channel")
    }

    MyControls.TextField {
        implicitWidth: 100
        text: channel
        inputMethodHints: Qt.ImhDigitsOnly
    }

    MyControls.Button {
        implicitWidth: 40
        text: qsTr("-")
        onClicked: {
            parent.destroy()
        }
    }
}

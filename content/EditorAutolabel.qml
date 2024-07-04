import QtQuick


Item {
    MyControls.VertTabBar {
        id: vertTabBarConfig
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.top: parent.top
        width: 180

        MyControls.TabButton {
            anchors.left: parent.left
            anchors.right: parent.right
            text: qsTr("General")
        }
    }
}
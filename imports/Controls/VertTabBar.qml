import QtQuick
import QtQuick.Controls

TabBar {
    id: control

    contentItem: ListView {
        model: control.contentModel
        currentIndex: control.currentIndex

        spacing: control.spacing
        orientation: ListView.Vertical   // <<-- VERTICAL
        boundsBehavior: Flickable.StopAtBounds
        flickableDirection: Flickable.AutoFlickIfNeeded
        snapMode: ListView.SnapToItem

        highlightMoveDuration: 0
        highlightRangeMode: ListView.ApplyRange
        preferredHighlightBegin: 40
        preferredHighlightEnd: height - 40
    }

    // background: Rectangle {
    //     color: "#FFFFFF"
    //     radius: 8
    // }
}

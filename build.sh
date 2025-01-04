#!/bin/bash

echo "QRC file generate"
pyside6-rcc resource.qrc -o src/utils/resource.py

echo "Start building..."
pyinstaller src/main.py \
--clean \
--strip \
--noconfirm \
--name midtool \
--add-data 'config:config' \
--add-binary 'lib/fingerprint/*.so:lib/fingerprint/' \
--add-data 'script:script' \
--add-data 'i18n:i18n' \
--add-data 'content/images/icon.png:.' \
--collect-all tzdata

cd dist/midtool/_internal || exit
echo "Delete useless lib and symlink"
rm -f \
libQt6Charts*.so.6 \
libQt6DataVisualization*.so.6 \
libQt6Egl*.so.6 \
libQt6Location.so.6 \
libQt6Pdf*.so.6 \
libQt6Positioning*.so.6 \
libQt6Quick3D*.so.6 \
libQt6QuickControls2Fusion*.so.6 \
libQt6QuickControls2Imagine*.so.6 \
libQt6QuickControls2Material*.so.6 \
libQt6QuickControls2Universal*.so.6 \
libQt6QuickEffects.so.6 \
libQt6QuickParticles.so.6 \
libQt6QuickShapes.so.6 \
libQt6QuickTest.so.6 \
libQt6QuickTimeline*.so.6 \
libQt6RemoteObjects*.so.6 \
libQt6Scxml*.so.6 \
libQt6Sensors*.so.6 \
libQt6ShaderTools.so.6 \
libQt6SpatialAudio.so.6 \
libQt6Sql.so.6 \
libQt6StateMachine*.so.6 \
libQt6Test.so.6 \
libQt6TextToSpeech.so.6 \
libQt6Web*.so.6 \
*Widgets.so.6 \
libQt63D*.so.6 \
libFLAC.so.8 \
libgstreamer-1.0.so.0 \
libpulse.so.0 \
libpulsecommon-*.so

echo "Delete useless Qt lib"
rm -f \
PySide6/*Widgets.abi3.so \
PySide6/Qt/lib/libQt6Charts*.so.6 \
PySide6/Qt/lib/libQt6DataVisualization*.so.6 \
PySide6/Qt/lib/libQt6Egl*.so.6 \
PySide6/Qt/lib/libQt6Location.so.6 \
PySide6/Qt/lib/libQt6Pdf*.so.6 \
PySide6/Qt/lib/libQt6Positioning*.so.6 \
PySide6/Qt/lib/libQt6Quick3D*.so.6 \
PySide6/Qt/lib/libQt6QuickControls2Fusion*.so.6 \
PySide6/Qt/lib/libQt6QuickControls2Imagine*.so.6 \
PySide6/Qt/lib/libQt6QuickControls2Material*.so.6 \
PySide6/Qt/lib/libQt6QuickControls2Universal*.so.6 \
PySide6/Qt/lib/libQt6QuickEffects.so.6 \
PySide6/Qt/lib/libQt6QuickParticles.so.6 \
PySide6/Qt/lib/libQt6QuickShapes.so.6 \
PySide6/Qt/lib/libQt6QuickTest.so.6 \
PySide6/Qt/lib/libQt6QuickTimeline*.so.6 \
PySide6/Qt/lib/libQt6RemoteObjects*.so.6 \
PySide6/Qt/lib/libQt6Scxml*.so.6 \
PySide6/Qt/lib/libQt6Sensors*.so.6 \
PySide6/Qt/lib/libQt6ShaderTools.so.6 \
PySide6/Qt/lib/libQt6SpatialAudio.so.6 \
PySide6/Qt/lib/libQt6Sql.so.6 \
PySide6/Qt/lib/libQt6StateMachine*.so.6 \
PySide6/Qt/lib/libQt6Test.so.6 \
PySide6/Qt/lib/libQt6TextToSpeech.so.6 \
PySide6/Qt/lib/libQt6Web*.so.6 \
PySide6/Qt/lib/*Widgets.so.6 \
PySide6/Qt/lib/libQt63D*.so.6

echo "Delete useless folder"
rm -rf \
*.dist-info \
PySide6/Qt/translations \
PySide6/Qt/plugins/egldeviceintegrations \
PySide6/Qt/plugins/qmltooling \
PySide6/Qt/qml/Qt3D \
PySide6/Qt/qml/Qt5Compat \
PySide6/Qt/qml/QtCharts \
PySide6/Qt/qml/QtDataVisualization \
PySide6/Qt/qml/QtLocation \
PySide6/Qt/qml/QtPositioning \
PySide6/Qt/qml/QtQuick3D \
PySide6/Qt/qml/QtRemoteObjects \
PySide6/Qt/qml/QtScxml \
PySide6/Qt/qml/QtSensors \
PySide6/Qt/qml/QtTest \
PySide6/Qt/qml/QtTextToSpeech \
PySide6/Qt/qml/QtWeb*

cd ../..
echo "Compress the folder to *.tar.xz pkg"
midtool_ver=$(python3 ../src/utils/version.py)
lsb=$(lsb_release -r -s)
tar -Jcf midtool_V"$midtool_ver"_"$lsb".tar.xz midtool
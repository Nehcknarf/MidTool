#!/bin/bash

echo "QRC file generate"
pyside6-rcc resource.qrc -o src/utils/resource.py

echo "Start building..."
pyinstaller src/main.py \
--clean \
--noconfirm \
--name midtool2 \
--add-data 'config:config' \
--add-data 'lib/fingerprint/*.so:lib/fingerprint/' \
--add-data 'script:script' \
--add-data 'i18n:i18n' \
--add-data 'content/images/icon.png:.' \
--collect-all tzdata

cd dist/midtool2/_internal || exit
echo "Delete useless lib and symlink"
rm -f \
libQt6Charts.so.6 \
libQt6ChartsQml.so.6 \
libQt6DataVisualization.so.6 \
libQt6DataVisualizationQml.so.6 \
libQt6Location.so.6 \
libQt6Pdf.so.6 \
libQt6PdfQuick.so.6 \
libQt6Positioning.so.6 \
libQt6PositioningQuick.so.6 \
libQt6Quick3D.so.6 \
libQt6Quick3DAssetImport.so.6 \
libQt6Quick3DAssetUtils.so.6 \
libQt6Quick3DEffects.so.6 \
libQt6Quick3DHelpers.so.6 \
libQt6Quick3DParticleEffects.so.6 \
libQt6Quick3DParticles.so.6 \
libQt6Quick3DRuntimeRender.so.6 \
libQt6Quick3DUtils.so.6 \
libQt6QuickTest.so.6 \
libQt6QuickTimeline.so.6 \
libQt6RemoteObjects.so.6 \
libQt6RemoteObjectsQml.so.6 \
libQt6Scxml.so.6 \
libQt6ScxmlQml.so.6 \
libQt6Sensors.so.6 \
libQt6SensorsQuick.so.6 \
libQt6ShaderTools.so.6 \
libQt6SpatialAudio.so.6 \
libQt6Sql.so.6 \
libQt6StateMachine.so.6 \
libQt6StateMachineQml.so.6 \
libQt6Test.so.6 \
libQt6TextToSpeech.so.6 \
libQt6WebChannel.so.6 \
libQt6WebEngineCore.so.6 \
libQt6WebEngineQuick.so.6 \
libQt6WebEngineQuickDelegatesQml.so.6 \
libQt63DAnimation.so.6 \
libQt63DCore.so.6 \
libQt63DExtras.so.6 \
libQt63DInput.so.6 \
libQt63DLogic.so.6 \
libQt63DQuick.so.6 \
libQt63DQuickAnimation.so.6 \
libQt63DQuickExtras.so.6 \
libQt63DQuickInput.so.6 \
libQt63DQuickRender.so.6 \
libQt63DQuickScene2D.so.6 \
libQt63DRender.so.6 \
libFLAC.so.8 \
libgstreamer-1.0.so.0 \
libpulse.so.0 \
libpulsecommon-*.so

echo "Delete useless Qt lib"
rm -f \
PySide6/Qt/lib/libQt6Charts.so.6 \
PySide6/Qt/lib/libQt6ChartsQml.so.6 \
PySide6/Qt/lib/libQt6DataVisualization.so.6 \
PySide6/Qt/lib/libQt6DataVisualizationQml.so.6 \
PySide6/Qt/lib/libQt6Location.so.6 \
PySide6/Qt/lib/libQt6Pdf.so.6 \
PySide6/Qt/lib/libQt6PdfQuick.so.6 \
PySide6/Qt/lib/libQt6Positioning.so.6 \
PySide6/Qt/lib/libQt6PositioningQuick.so.6 \
PySide6/Qt/lib/libQt6Quick3D.so.6 \
PySide6/Qt/lib/libQt6Quick3DAssetImport.so.6 \
PySide6/Qt/lib/libQt6Quick3DAssetUtils.so.6 \
PySide6/Qt/lib/libQt6Quick3DEffects.so.6 \
PySide6/Qt/lib/libQt6Quick3DHelpers.so.6 \
PySide6/Qt/lib/libQt6Quick3DParticleEffects.so.6 \
PySide6/Qt/lib/libQt6Quick3DParticles.so.6 \
PySide6/Qt/lib/libQt6Quick3DRuntimeRender.so.6 \
PySide6/Qt/lib/libQt6Quick3DUtils.so.6 \
PySide6/Qt/lib/libQt6QuickTest.so.6 \
PySide6/Qt/lib/libQt6QuickTimeline.so.6 \
PySide6/Qt/lib/libQt6RemoteObjects.so.6 \
PySide6/Qt/lib/libQt6RemoteObjectsQml.so.6 \
PySide6/Qt/lib/libQt6Scxml.so.6 \
PySide6/Qt/lib/libQt6ScxmlQml.so.6 \
PySide6/Qt/lib/libQt6Sensors.so.6 \
PySide6/Qt/lib/libQt6SensorsQuick.so.6 \
PySide6/Qt/lib/libQt6ShaderTools.so.6 \
PySide6/Qt/lib/libQt6SpatialAudio.so.6 \
PySide6/Qt/lib/libQt6Sql.so.6 \
PySide6/Qt/lib/libQt6StateMachine.so.6 \
PySide6/Qt/lib/libQt6StateMachineQml.so.6 \
PySide6/Qt/lib/libQt6Test.so.6 \
PySide6/Qt/lib/libQt6TextToSpeech.so.6 \
PySide6/Qt/lib/libQt6WebChannel.so.6 \
PySide6/Qt/lib/libQt6WebEngineCore.so.6 \
PySide6/Qt/lib/libQt6WebEngineQuick.so.6 \
PySide6/Qt/lib/libQt6WebEngineQuickDelegatesQml.so.6 \
PySide6/Qt/lib/libQt63DAnimation.so.6 \
PySide6/Qt/lib/libQt63DCore.so.6 \
PySide6/Qt/lib/libQt63DExtras.so.6 \
PySide6/Qt/lib/libQt63DInput.so.6 \
PySide6/Qt/lib/libQt63DLogic.so.6 \
PySide6/Qt/lib/libQt63DQuick.so.6 \
PySide6/Qt/lib/libQt63DQuickAnimation.so.6 \
PySide6/Qt/lib/libQt63DQuickExtras.so.6 \
PySide6/Qt/lib/libQt63DQuickInput.so.6 \
PySide6/Qt/lib/libQt63DQuickRender.so.6 \
PySide6/Qt/lib/libQt63DQuickScene2D.so.6 \
PySide6/Qt/lib/libQt63DRender.so.6

echo "Delete useless folder"
rm -rf \
*.dist-info \
PySide6/Qt/translations \
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
PySide6/Qt/qml/QtWebChannel \
PySide6/Qt/qml/QtWebEngine \
PySide6/Qt/plugins/qmltooling

cd ../..
echo "Compress the folder to *.tar.bz2 pkg"
midtool_ver=$(python3 ../src/utils/version.py)
lsb=$(lsb_release -r -s)
tar -zvcf midtool_"$midtool_ver"_"$lsb".tar.gz midtool2

#!/bin/bash

echo "QRC file generate"
pyside6-rcc resource.qrc -o src/utils/resource.py

#mamba install -y libpython-static
#mamba install c-compiler cxx-compiler

echo "Start building..."
python -m nuitka src/main.py \
    --standalone \
    --output-dir=dist \
    --remove-output \
    --product-name=midtool \
    --output-filename=midtool \
    --include-data-dir=config=config \
    --include-data-files="lib/fingerprint/*.so=lib/fingerprint/" \
    --include-data-dir=script=script \
    --include-data-dir=i18n=i18n \
    --include-data-files=content/images/icon.png=. \
    --windows-icon-from-ico=content/images/icon.png \
    --include-package-data=tzdata \
    --enable-plugin=pyside6 \
    --assume-yes-for-downloads
#!/bin/bash

soft_pkg=$1
if [ "$(echo $LANG | grep zh_CN)" != "" ]; then
    echo 获取文件路径: $soft_pkg 开始升级...
    if [ "$(echo $soft_pkg | grep ".tar.gz")" != "" ]; then
        mkdir -p /nubomed/tmp
        rm -rf /nubomed/tmp/*
        echo "开始解压升级包..."
        tar -zxvf $soft_pkg -C /nubomed/tmp/ >>/dev/null
        echo "升级包解压完成..."
        if [ "$(ls /nubomed/tmp/ | grep "update.sh")" != "" ]; then
            echo "开始升级..."
            bash /nubomed/tmp/update.sh
            echo "升级完成，请检查！！！"
        else
            echo "开始升级..."
            bash /nubomed/tmp/upgrade.sh
            echo "升级完成，请检查！！！"
        fi
    elif [ "$(echo $soft_pkg | grep ".zip")" != "" ]; then
        mkdir -p /nubomed/tmp
        rm -rf /nubomed/tmp/*
        echo "开始解压升级包..."
        unzip $soft_pkg -d /nubomed/tmp/ >>/dev/null
        sh=$(find /nubomed/tmp/ -name "*.sh")
        echo $sh
        echo "开始升级..."
        bash $sh
        echo "执行完成，请检查！！！"
    elif [ "$(echo $soft_pkg | grep ".sh")" != "" ]; then 
        echo "开始执行..."
        bash $soft_pkg
        echo "执行完成，请检查！！！"
    else
        echo "未知类型,请重新选择！！！"
    fi
else
    if [ "$(echo $soft_pkg | grep ".tar.gz")" != "" ]; then
        mkdir -p /nubomed/tmp
        rm -rf /nubomed/tmp/*
        echo "Start decompressing the upgrade package..."
        tar -zxvf $soft_pkg -C /nubomed/tmp/ >>/dev/null
        echo "Upgrade package decompression completed..."
        if [ "$(ls /nubomed/tmp/ | grep "update.sh")" != "" ]; then
            echo "Start Upgrade..."
            bash /nubomed/tmp/update.sh
            echo "Upgrade completed, please check！！！"
        else
            echo "Start Upgrade..."
            bash /nubomed/tmp/upgrade.sh
            echo "Upgrade completed, please check！！！"
        fi
    elif [ "$(echo $soft_pkg | grep ".zip")" != "" ]; then
        mkdir -p /nubomed/tmp
        rm -rf /nubomed/tmp/*
        echo "Start decompressing the upgrade package..."
        unzip $soft_pkg -d /nubomed/tmp/ >>/dev/null
        sh=$(find /nubomed/tmp/ -name "*.sh")
        echo $sh
        echo "Start Upgrade..."
        bash $sh
        echo "Upgrade completed, please check！！！"
    elif [ "$(echo $soft_pkg | grep ".sh")" != "" ]; then 
        echo "Start Upgrade..."
        bash $soft_pkg
        echo "Upgrade completed, please check！！！"
    else
        echo "Unknown type, please reselect！！！"
    fi
fi


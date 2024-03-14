#!/bin/bash

if [ "$(who i am | grep nuobo)" != "" ]; then
   sysuser="nuobo"
   passwd="Nb123456"
else
   sysuser="nubomed"
   passwd="Nb@123456"
fi

if [ "$(echo $LANG | grep zh_CN)" != "" ]; then
   hint1="请先配置内网网卡IP，再设置网络优先级！！！"
   hint2="设置完成"
else
   hint1="Please configure the internal network card IP first, and then set the network priority!!!"
   hint2="Setting completed!!!"
fi


file=$(echo $passwd | sudo -S grep -R "enp2s0" /etc/NetworkManager/system-connections | awk -F ":" '{print $1}')

if [ "$file" == "" ]; then
   echo $hint1
   exit 1
fi

flag=$(echo $passwd | sudo -S cat "$file" | grep "never-default=true")

if [ "$file" != "" ] && [ "$flag" == "" ]; then
   echo $passwd | sudo -S sed -i '/ipv4/a\never-default=true' "$file"
   echo $passwd | sudo -S systemctl restart network-manager
fi

echo $hint2
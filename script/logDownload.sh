#!/bin/bash

download_dir=$1
start_time=$(date -d "$2 -1 days" +%s)
end_time=$(date -d $3 +%s)

now_time=$(date +%Y%m%d%H%M%S)


if [ -d /nubomed/midpkg/drug-middleware/ ]; then
   passwd="Nb123456"
   business_logdir="/nubomed/midpkg/logs"
else
   passwd="Nb@123456"
   business_logdir="/nubomed/consumable-service/logs"
fi

if [ -d /nubomed/ecart-service/ ]; then
   passwd="Nb@123456"
   business_logdir="/nubomed/ecart-service/logs"
fi

if [ "$4" = "1" ]; then
   for element in $(ls $business_logdir); do
      if [ "$(stat -c %Y "$business_logdir/$element")" -gt "$start_time" ] && [ "$(stat -c %Y "$business_logdir/$element")" -lt "$end_time" ]; then
         echo $element
         zip -r $business_logdir/business_logs$now_time.zip $business_logdir/$element
      fi
   done
   mv $business_logdir/business_logs$now_time.zip $download_dir
elif [ "$4" = "2" ]; then
   for element in $(ls /var/log/syslog*); do
      if [ "$(stat -c %Y "$element")" -gt "$start_time" ] && [ "$(stat -c %Y "$element")" -lt "$end_time" ]; then
         echo $element
         echo $passwd | sudo -S zip -r /var/log/sys_logs$now_time.zip $element
      fi
   done
   echo $passwd | sudo -S mv /var/log/sys_logs$now_time.zip $download_dir
   echo $passwd | sudo -S chown -R nuobo:nuobo $download_dir/sys_logs$now_time.zip
   
   for element in $(ls /var/log/kern*); do
      if [ "$(stat -c %Y "$element")" -gt "$start_time" ] && [ "$(stat -c %Y "$element")" -lt "$end_time" ]; then
         echo $element
         echo $passwd | sudo -S zip -r /var/log/sys_logs$now_time.zip $element
      fi
   done
   echo $passwd | sudo -S mv /var/log/sys_logs$now_time.zip $download_dir
   echo $passwd | sudo -S chown -R nuobo:nuobo $download_dir/sys_logs$now_time.zip
   
   for element in $(ls /var/log/boot*); do
      if [ "$(stat -c %Y "$element")" -gt "$start_time" ] && [ "$(stat -c %Y "$element")" -lt "$end_time" ]; then
         echo $element
         echo $passwd | sudo -S zip -r /var/log/sys_logs$now_time.zip $element
      fi
   done
   echo $passwd | sudo -S mv /var/log/sys_logs$now_time.zip $download_dir
   echo $passwd | sudo -S chown -R nuobo:nuobo $download_dir/sys_logs$now_time.zip
else
   echo "类型错误"
   exit 1
fi










#!/bin/bash

download_dir=$1
start_time=$(date -d "$2 -1 days" +%s)
end_time=$(date -d $3 +%s)

now_time=$(date +%Y%m%d%H%M%S)


if [ -d /nubomed/midpkg/drug-middleware/ ]; then
   username="nuobo"
   passwd="Nb123456"
   business_logdir="/nubomed/midpkg/logs"
else
   username="nubomed"
   passwd="Nb@123456"
   business_logdir="/nubomed/consumable-cabinet-service/logs"
fi

if [ -d /nubomed/ecart-service/ ]; then
   username="nubomed"
   passwd="Nb@123456"
   business_logdir="/nubomed/ecart-service/logs"
fi

if [ "$4" = "1" ]; then
   for element in $(ls $business_logdir); do
      if [ "$(stat -c %Y "$business_logdir/$element")" -ge "$start_time" ] && [ "$(stat -c %Y "$business_logdir/$element")" -le "$end_time" ]; then
         echo $element
         zip -r $business_logdir/business_logs$now_time.zip $business_logdir/$element >>/dev/null
      fi
   done
   if [ -f $business_logdir/business_logs$now_time.zip ]; then
      mv $business_logdir/business_logs$now_time.zip $download_dir
   else
      echo "The selected condition range has no logs"
   fi
elif [ "$4" = "2" ]; then
   echo $passwd | sudo -S touch /var/log/sys_logs$now_time.zip
   for element in $(ls /var/log/syslog*); do
      if [ "$(stat -c %Y "$element")" -ge "$start_time" ] && [ "$(stat -c %Y "$element")" -le "$end_time" ]; then
         echo $passwd | sudo -S zip -r /var/log/sys_logs$now_time.zip $element >>/dev/null
      fi
   done
   
   for element in $(ls /var/log/kern*); do
      if [ "$(stat -c %Y "$element")" -ge "$start_time" ] && [ "$(stat -c %Y "$element")" -le "$end_time" ]; then
         echo $passwd | sudo -S zip -r /var/log/sys_logs$now_time.zip $element >>/dev/null
      fi
   done
   
   for element in $(ls /var/log/boot*); do
      if [ "$(stat -c %Y "$element")" -ge "$start_time" ] && [ "$(stat -c %Y "$element")" -le "$end_time" ]; then
         echo $passwd | sudo -S zip -r /var/log/sys_logs$now_time.zip $element >>/dev/null
      fi
   done

   if [ -f /var/log/sys_logs$now_time.zip ]; then
      echo $passwd | sudo -S mv /var/log/sys_logs$now_time.zip $download_dir
      echo $passwd | sudo -S chown -R $username:$username $download_dir/sys_logs$now_time.zip >>/dev/null
   else
      echo "The selected condition range has no logs"
   fi

else
   echo "type error"
   exit 1
fi










#!/bin/bash

APP_ID=$1
SDK_KEY=$2
activeKey=$3

cur_dir=$(cd $(dirname "${BASH_SOURCE[0]}") && pwd )

clear   

echo APP_ID:$1
echo SDK_KEY:$2
echo activeKey:$3


if [ "$(find /nubomed/ -name "drug-middleware")" != "" ]; then
	source /etc/profile
fi
if [ "$(find /nubomed/ -name "consumable-cabinet-service")" != "" ]; then
	export LD_LIBRARY_PATH=.:/nubomed/libs
fi

if [ "$(ps -ef | grep arsoftActiveTool | grep -v "grep")" = "" ]; then
	nohup java -jar $cur_dir/arsoftActiveTool-0.0.1-SNAPSHOT.jar --server.port=32201 >/dev/null 2>&1 &
fi
printf "正在启动虹软在线激活服务,请稍后..."
for (( i = 0; i < 15; i++ )); do
   if [ "$(netstat -ano | grep 32201)" != "" ]; then
      sleep 10s
      break
   else
      sleep 2s 
   fi
done 

echo "正在执行激活,请稍后..."
curl --location "http://127.0.0.1:32201/system/activeFaceEngin?appId=$1&sdkKey=$2&activeKey=$3" 1>$cur_dir/flag.txt 2>>debug.log

ps -ef | grep arsoftActiveTool | awk '{print $2}' | awk 'NR==1' | xargs kill -9

flag=$(cat $cur_dir/flag.txt)
echo $flag
case $flag in
	0)
		echo "激活成功"
		;;
	90114)	
		echo "已激活"
		;;
	90115)
		echo "未激活"
		;;
	90117)	
		echo "激活文件与SDK类型不匹配，请确认使用的sdk"
		;;
	90120)
		echo "参数为空"
		;;
	28673)
		echo "无效的AppId"
		;;
	28674)
		echo "无效的SDKkey"
		;;
	28675)
		echo "AppId和SDKKey不匹配"
		;;
	28676)
		echo "SDKKey和使用的SDK不匹配,请检查入参"
		;;
	28677)
		echo "系统版本不被当前SDK所支持"
		;;
	28678)
		echo "SDK有效期过期，需要重新下载更新" 
		;;
	90120)
		echo "参数为空"
		;;
	98308)
		echo "ACTIVEKEY激活码与APPID、SDKKEY不匹配"
		;;
	98309)
		echo "ACTIVEKEY激活码已经被使用"
		;;
	98310)
		echo "ACTIVEKEY激活码信息异常" 
		;;
	98311)
		echo "ACTIVEKEY激活码与APPID不匹配"
		;;
	98312)
		echo "SDK与激活文件版本不匹配"
		;;
	98313)
		echo "ACTIVEKEY激活码已过期" 
		;;
	*)
		echo "其他错误"
	   ;;
esac
rm $cur_dir/flag.txt

if [ "$flag" = "0" ]; then
	if [ "$(find /nubomed/ -name "drug-middleware")" != "" ]; then
		cp $cur_dir/ArcFacePro64.dat /nubomed/midpkg/
	fi
   if [ "$(find /nubomed/ -name "consumable-cabinet-service")" != "" ]; then
		cp $cur_dir/ArcFacePro64.dat /nubomed/consumable-cabinet-service/conf
	fi
	rm $cur_dir/ArcFacePro64.dat
fi

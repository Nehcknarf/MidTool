#!/bin/bash

APP_ID=$1
SDK_KEY=$2
activeKey=$3

cur_dir=$(cd $(dirname "${BASH_SOURCE[0]}") && pwd )


clear   

echo APP_ID:$1
echo SDK_KEY:$2
echo activeKey:$3


if [  -d "/nubomed/midpkg/drug-middleware/" ]; then
	export LD_LIBRARY_PATH=.:/nubomed/midpkg/opencv-lib
	cabinettype="drug"
fi
if [  -d "/nubomed/consumable-cabinet-service/" ]; then
	export LD_LIBRARY_PATH=.:/nubomed/libs
	cabinettype="consumable"	
fi
if [  -d "/nubomed/ecart-service/" ]; then
	export LD_LIBRARY_PATH=.:/nubomed/libs
	cabinettype="ecart"	
fi

if [ "$(echo $LANG | grep zh_CN)" != "" ]; then
	case $cabinettype in
		drug)
			echo "识别系统类型为：药柜4.1"
			;;
		consumable)
			echo "识别系统类型为：耗材4.1"
			;;
		ecart)
			echo "识别系统类型为：Y6000抢救车"
			;;
		*)
			echo "终端系统类型检测异常,请检查终端环境！！！"
			exit 1
		   ;;
	esac

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


	echo $(date +%Y-%m-%d" "%H:%M:%S:) >>$cur_dir/debug.log
	echo "正在执行激活,请稍后..."
	curl --location "http://127.0.0.1:32201/system/activeFaceEngin?appId=$1&sdkKey=$2&activeKey=$3" 1>$cur_dir/flag.txt 2>>$cur_dir/debug.log

	ps -ef | grep arsoftActiveTool | awk '{print $2}' | awk 'NR==1' | xargs kill -9

	flag=$(cat $cur_dir/flag.txt)

	echo $(date +%Y-%m-%d" "%H:%M:%S:) $flag >>$cur_dir/debug.log

	case $flag in
		0)
			echo "code:$flag,激活成功"
			;;
		90114)	
			echo "code:$flag,已激活"
			;;
		90115)
			echo "code:$flag,未激活"
			;;
		90117)	
			echo "code:$flag,激活文件与SDK类型不匹配"
			;;
		90120)
			echo "code:$flag,参数为空"
			;;
		28673)
			echo "code:$flag,无效的AppId"
			;;
		28674)
			echo "code:$flag,无效的SDKkey"
			;;
		28675)
			echo "code:$flag,AppId和SDKKey不匹配"
			;;
		28676)
			echo "code:$flag,SDKKey和使用的SDK不匹配,请检查入参"
			;;
		28677)
			echo "code:$flag,系统版本不被当前SDK所支持"
			;;
		28678)
			echo "code:$flag,SDK有效期过期，需要重新下载更新" 
			;;
		98308)
			echo "code:$flag,ACTIVEKEY激活码与APPID、SDKKEY不匹配"
			;;
		98309)
			echo "code:$flag,ACTIVEKEY激活码已经被使用"
			;;
		98310)
			echo "code:$flag,ACTIVEKEY激活码信息异常" 
			;;
		98311)
			echo "code:$flag,ACTIVEKEY激活码与APPID不匹配"
			;;
		98312)
			echo "code:$flag,SDK与激活文件版本不匹配"
			;;
		98313)
			echo "code:$flag,ACTIVEKEY激活码已过期" 
			;;
		*)
			echo "code:$flag,其他错误"
		   ;;
	esac
fi


if [ "$(echo $LANG | grep zh_CN)" = "" ]; then
	case $cabinettype in
		drug)
			echo "The current project type：drug"
			;;
		consumable)
			echo "The current project type：consumable"
			;;
		ecart)
			echo "The current project type：ecart"
			;;
		*)
			echo "Abnormal terminal system type detection, please check the terminal environment!!!"
			exit 1
		   ;;
	esac

	if [ "$(ps -ef | grep arsoftActiveTool | grep -v "grep")" = "" ]; then
		nohup java -jar $cur_dir/arsoftActiveTool-0.0.1-SNAPSHOT.jar --server.port=32201 >/dev/null 2>&1 &
	fi

	printf "Starting the Hongsoft online activation service, please wait..."
	for (( i = 0; i < 15; i++ )); do
	   if [ "$(netstat -ano | grep 32201)" != "" ]; then
	      sleep 10s
	      break
	   else
	      sleep 2s 
	   fi
	done 


	echo $(date +%Y-%m-%d" "%H:%M:%S:) >>$cur_dir/debug.log
	echo "Performing activation, please wait..."
	curl --location "http://127.0.0.1:32201/system/activeFaceEngin?appId=$1&sdkKey=$2&activeKey=$3" 1>$cur_dir/flag.txt 2>>$cur_dir/debug.log

	ps -ef | grep arsoftActiveTool | awk '{print $2}' | awk 'NR==1' | xargs kill -9

	flag=$(cat $cur_dir/flag.txt)

	echo $(date +%Y-%m-%d" "%H:%M:%S:) $flag >>$cur_dir/debug.log

	case $flag in
		0)
			echo "code:$flag,Activation successful"
			;;
		90114)	
			echo "code:$flag,Actived"
			;;
		90115)
			echo "code:$flag,not active"
			;;
		90117)	
			echo "code:$flag,Activation file does not match SDK type"
			;;
		90120)
			echo "code:$flag,Parameter is empty"
			;;
		28673)
			echo "code:$flag,Invalid AppId"
			;;
		28674)
			echo "code:$flag,Invalid SDK key"
			;;
		28675)
			echo "code:$flag,AppId和SDKKey不匹配"
			;;
		28676)
			echo "code:$flag,AppId and SDKKey do not match"
			;;
		28677)
			echo "code:$flag,The system version is not supported by the current SDK"
			;;
		28678)
			echo "code:$flag,SDK expiration date, update needs to be downloaded again" 
			;;
		98308)
			echo "code:$flag,ACTIVEKEY activation code does not match APPID, SDKKEY"
			;;
		98309)
			echo "code:$flag,The ACTIVEKEY activation code has been used"
			;;
		98310)
			echo "code:$flag,ACTIVEKEY activation code information is abnormal" 
			;;
		98311)
			echo "code:$flag,ACTIVEKEY activation code does not match APPID"
			;;
		98312)
			echo "code:$flag,SDK and activation file version mismatch"
			;;
		98313)
			echo "code:$flag,ACTIVEKEY activation code has expired" 
			;;
		*)
			echo "code:$flag,Other errors"
		   ;;
	esac
fi

rm $cur_dir/flag.txt

if [ "$flag" = "0" ]; then
	case $cabinettype in
		drug)
			mv $cur_dir/ArcFacePro64.dat /nubomed/midpkg/
			;;
		consumable)
			mv $cur_dir/ArcFacePro64.dat /nubomed/consumable-cabinet-service/
			;;
		ecart)
			mv $cur_dir/ArcFacePro64.dat /nubomed/ecart-service/
			;;
	esac
fi
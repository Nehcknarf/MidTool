#!/bin/bash

# 脚本目标：配置Chrony客户端，并可选地让它成为本地网络的NTP服务器。
# 兼容性：自动检测新版（使用 sources.d/conf.d 目录）和旧版（使用单一 chrony.conf）的Chrony配置。
# v2: 修复了在某些系统上 sed 命令的兼容性问题。

# --- 脚本设置 ---
# 如果任何命令失败，立即退出，防止部分配置生效
set -e

# --- 变量定义 ---
NTP_SERVER=$1
# 本地网络，如果需要为其他设备提供时间服务，请修改这个网段
LOCAL_NETWORK="192.168.0.0/24"

# --- 1. 输入检查 ---
if [ -z "$NTP_SERVER" ]; then
  echo "错误：缺少NTP服务器地址。"
  echo "用法: $0 <ntp_server_address>"
  exit 1
fi

# --- 2. 确保 Chrony 已安装 (适用于 Debian/Ubuntu) ---
if ! dpkg -l | grep -qw chrony; then
  echo "Chrony 未安装，正在尝试安装..."
  # 在非交互模式下，最好先运行 apt update
  apt-get update && apt-get install -y chrony
  if [ $? -ne 0 ]; then
    echo "Chrony 安装失败，请手动安装后重试。"
    exit 1
  fi
fi

# --- 3. 核心逻辑：检测配置结构并应用配置 ---
echo "正在配置 Chrony..."

# 检查是否存在新版的 sources.d 目录
if [ -d "/etc/chrony/sources.d" ]; then
  # --- 新版 Chrony 配置逻辑 ---
  echo "检测到新版 Chrony 配置结构。"

  # 配置上游 NTP 服务器
  echo "server $NTP_SERVER iburst prefer" > /etc/chrony/sources.d/local-ntp-server.sources

  # 配置本地授时
  cat > /etc/chrony/conf.d/local-ntp-server.conf << EOF
# 允许指定网段的设备从本机同步时间
allow $LOCAL_NETWORK
# 当无法连接到互联网NTP服务器时，本机作为第10层时间源
local stratum 10
EOF

else
  # --- 旧版 Chrony 配置逻辑 ---
  echo "检测到旧版 Chrony 配置结构。"

  # 确定主配置文件路径
  CONF_FILE="/etc/chrony.conf"
  if [ ! -f "$CONF_FILE" ]; then
    # 某些发行版的路径不同
    CONF_FILE="/etc/chrony/chrony.conf"
  fi

  if [ ! -f "$CONF_FILE" ]; then
    echo "错误：找不到 Chrony 配置文件 (chrony.conf 或 chrony/chrony.conf)。"
    exit 1
  fi

  echo "正在修改配置文件: $CONF_FILE"

  # 使用两条简单命令替换之前复杂的 sed 命令，以保证最大兼容性
  echo "正在注释掉旧的 server/pool 配置..."
  sed -i 's/^ *pool/#pool/g' "$CONF_FILE"
  sed -i 's/^ *server/#server/g' "$CONF_FILE"

  # b. 删除之前可能由本脚本添加的配置，防止重复
  echo "正在清理旧的脚本配置..."
  sed -i "/^server.*prefer$/d" "$CONF_FILE"
  sed -i "/^allow/d" "$CONF_FILE"
  sed -i "/^local stratum 10/d" "$CONF_FILE"

  # c. 在文件末尾追加新配置
  echo "正在追加新配置..."
  {
    echo "" # 加一个空行，格式更清晰
    echo "server $NTP_SERVER iburst prefer"
    echo "allow $LOCAL_NETWORK"
    echo "local stratum 10"
  } >> "$CONF_FILE"

fi

# --- 4. 重启服务使配置生效 ---
echo "重启 Chrony 服务..."
systemctl restart chrony

# --- 5. 提示用户检查状态 ---
echo "Chrony 配置完成并已重启。"
echo "等待一两分钟后，您可以使用 'chronyc sources' 或 'chronyc tracking' 命令检查同步状态。"

exit 0
#!/bin/bash

# 配置变量 (与启动脚本一致)
HOTSPOT_SSID="DistCapsule_Box"

echo "=== 正在关闭 Pi 5 热点并清理进程 ==="

# 检查 root
if [ "$EUID" -ne 0 ]; then
  echo "❌ 请使用 sudo 运行此脚本"
  exit 1
fi

# 1. 停止 NetworkManager 链路
echo "1. 正在关闭 Wi-Fi 热点链路..."
nmcli con down "$HOTSPOT_SSID" 2>/dev/null

# 2. 杀掉手动启动的 dnsmasq 进程
echo "2. 正在停止 DHCP 服务 (dnsmasq)..."
# 使用 -f 匹配启动命令中的特征字符串，确保不误杀系统其他 dnsmasq
pkill -f "dnsmasq.*$HOTSPOT_SSID"

# 3. (可选) 恢复 wlan0 的自动连接
echo "3. 恢复网络接口状态..."
nmcli dev set wlan0 managed yes

echo "==========================================="
echo "✅ 热点已彻底关闭。"
echo "现在你可以重新连接常规 Wi-Fi 或进行其他操作。"
echo "==========================================="

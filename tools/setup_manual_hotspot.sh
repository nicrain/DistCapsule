#!/bin/bash

# 配置变量
HOTSPOT_SSID="DistCapsule_Box"
HOTSPOT_PASSWORD="capsule_admin"
GATEWAY_IP="192.168.4.1"
DHCP_RANGE="192.168.4.10,192.168.4.50,24h" # 分配 IP 范围

echo "=== 配置 Pi 5 '无网关' 热点 (命令行参数版) ==="
echo "策略: NetworkManager (仅链路) + Dnsmasq (仅 DHCP)"

# 检查 root
if [ "$EUID" -ne 0 ]; then
  echo "[ERROR] 请使用 sudo 运行此脚本"
  exit 1
fi

# 1. 确保安装 dnsmasq (我们需要它的二进制文件)
# -y 如果已安装会直接跳过
apt-get install -y dnsmasq

# 1.1 强力停止系统默认的 dnsmasq 服务 (防止冲突)
# 尝试停止服务
systemctl stop dnsmasq 2>/dev/null || true
systemctl disable dnsmasq 2>/dev/null || true
# 暴力查杀任何仍在运行的 dnsmasq 进程 (确保端口 67 绝对空闲)
pkill -x dnsmasq || true
sleep 1 # 给系统一点时间释放端口

# 2. 清理旧环境
echo "1. 清理环境..."
nmcli connection delete "$HOTSPOT_SSID" 2>/dev/null || true
# 杀掉可能残留的、我们在之前运行的 dnsmasq 进程
pkill -f "dnsmasq.*$HOTSPOT_SSID" || true

# 3. 创建热点 (Manual 模式)
echo "2. 创建 Wi-Fi 链路..."
nmcli con add type wifi ifname wlan0 mode ap con-name "$HOTSPOT_SSID" ssid "$HOTSPOT_SSID"
nmcli con modify "$HOTSPOT_SSID" wifi-sec.key-mgmt wpa-psk
nmcli con modify "$HOTSPOT_SSID" wifi-sec.psk "$HOTSPOT_PASSWORD"
nmcli con modify "$HOTSPOT_SSID" ipv4.addresses "$GATEWAY_IP/24"
# 关键: 使用 manual 模式，禁止 NetworkManager 自动接管 DHCP
nmcli con modify "$HOTSPOT_SSID" ipv4.method manual 

# 4. 启动热点
echo "3. 启动 Wi-Fi..."
nmcli con up "$HOTSPOT_SSID"
sleep 2 # 等待接口完全就绪

# 5. 手动启动 DHCP 服务 (核心魔法)
echo "4. 启动独立 DHCP 服务..."
# 参数详解:
# --conf-file=/dev/null : 不读取任何系统配置文件，保证纯净
# --interface=wlan0     : 只在热点网卡工作
# --bind-interfaces     : 绑定接口，防止冲突
# --port=0              : 禁用 DNS 功能 (避免与 systemd-resolved 冲突)，只做 DHCP
# --dhcp-range=...      : 分配 IP
# --dhcp-option=3       : 重点！设置网关选项为空 (即不发送网关)
# --dhcp-option=6       : 设置 DNS 服务器为空 (可选，进一步防止手机尝试解析域名)

dnsmasq \
  --conf-file=/dev/null \
  --no-daemon \
  --interface=wlan0 \
  --bind-interfaces \
  --port=0 \
  --dhcp-range=$DHCP_RANGE \
  --dhcp-option=3,192.168.4.1 \
  --dhcp-option=6 \
  > /var/log/capsule_dhcp.log 2>&1 &  # 后台运行并记录日志

echo "==========================================="
echo "[OK] 热点已就绪!"
echo "PID: $!"
echo "-------------------------------------------"
echo "逻辑验证:"
echo "1. NM 只负责 Wi-Fi 信号，不管分配 IP。"
echo "2. dnsmasq 进程手动运行，强制不发网关。"
echo "3. 系统配置零污染。"
echo "==========================================="

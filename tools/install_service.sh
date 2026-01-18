#!/bin/bash

SERVICE_NAME="capsule"
USER_NAME=$USER
# 获取脚本所在目录的上一级作为项目根目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PYTHON_EXEC=$(which python3)

echo "--- 胶囊分配器 开机自启安装脚本 ---"
echo "项目根目录: $PROJECT_ROOT"
echo "执行用户: $USER_NAME"
echo "Python路径: $PYTHON_EXEC"

# 1. 创建 systemd 服务文件内容 (主程序)
SERVICE_CONTENT="[Unit]
Description=Smart Capsule Dispenser Service
After=network.target multi-user.target capsule_hotspot.service

[Service]
Type=simple
User=$USER_NAME
WorkingDirectory=$PROJECT_ROOT
ExecStart=$PYTHON_EXEC $PROJECT_ROOT/main.py
Restart=always
RestartSec=5
# 确保输出即时刷新到日志
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target"

# 1.1 创建 systemd 服务文件内容 (热点 & DHCP)
HOTSPOT_SERVICE_NAME="capsule_hotspot"
HOTSPOT_SERVICE_CONTENT="[Unit]
Description=DistCapsule Hotspot & DHCP Controller
After=network.target

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/bin/bash $PROJECT_ROOT/tools/setup_manual_hotspot.sh
ExecStop=/bin/bash $PROJECT_ROOT/tools/stop_hotspot.sh

[Install]
WantedBy=multi-user.target"

# 1.2 创建 systemd 服务文件内容 (API 服务器)
API_SERVICE_NAME="capsule_api"
API_SERVICE_CONTENT="[Unit]
Description=DistCapsule API Server (FastAPI)
After=network.target capsule_hotspot.service

[Service]
Type=simple
User=$USER_NAME
WorkingDirectory=$PROJECT_ROOT
# 使用 uvicorn 启动服务器，绑定 0.0.0.0:8000
ExecStart=$PYTHON_EXEC -m uvicorn api.server:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target"

# 2. 写入系统目录 (需要 sudo 权限)
echo "正在创建主服务文件 /etc/systemd/system/${SERVICE_NAME}.service ..."
echo "$SERVICE_CONTENT" | sudo tee /etc/systemd/system/${SERVICE_NAME}.service > /dev/null

echo "正在创建热点服务文件 /etc/systemd/system/${HOTSPOT_SERVICE_NAME}.service ..."
echo "$HOTSPOT_SERVICE_CONTENT" | sudo tee /etc/systemd/system/${HOTSPOT_SERVICE_NAME}.service > /dev/null

echo "正在创建 API 服务文件 /etc/systemd/system/${API_SERVICE_NAME}.service ..."
echo "$API_SERVICE_CONTENT" | sudo tee /etc/systemd/system/${API_SERVICE_NAME}.service > /dev/null

# 3. 重新加载守护进程
echo "重新加载 systemd..."
sudo systemctl daemon-reload

# 4. 启用并启动服务
echo "启用开机自启 (热点)..."
sudo systemctl enable $HOTSPOT_SERVICE_NAME
echo "启用开机自启 (API)..."
sudo systemctl enable $API_SERVICE_NAME
echo "启用开机自启 (主程序)..."
sudo systemctl enable $SERVICE_NAME

echo "正在尝试启动服务..."
# 按顺序启动：网络 -> API -> 硬件
sudo systemctl restart $HOTSPOT_SERVICE_NAME
sudo systemctl restart $API_SERVICE_NAME
sudo systemctl restart $SERVICE_NAME

# 5. 检查状态
echo "--- 服务状态检查 ---"
sleep 2
if systemctl is-active --quiet $HOTSPOT_SERVICE_NAME; then
    echo "[OK] 热点服务启动成功！"
else
    echo "[ERROR] 热点服务启动失败，请检查日志："
    echo "  sudo journalctl -u $HOTSPOT_SERVICE_NAME -n 20"
fi

if systemctl is-active --quiet $API_SERVICE_NAME; then
    echo "[OK] API 服务启动成功！"
else
    echo "[ERROR] API 服务启动失败，请检查日志："
    echo "  sudo journalctl -u $API_SERVICE_NAME -n 20"
fi

if systemctl is-active --quiet $SERVICE_NAME; then
    echo "[OK] 主程序服务启动成功！"
    echo "你可以使用以下命令查看日志："
    echo "  sudo journalctl -u $SERVICE_NAME -f"
    echo ""
    echo "如果需要停止服务进行调试："
    echo "  sudo systemctl stop $SERVICE_NAME"
else
    echo "[ERROR] 服务启动失败，请检查日志："
    echo "  sudo journalctl -u $SERVICE_NAME -n 20"
fi

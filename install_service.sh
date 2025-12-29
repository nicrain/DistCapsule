#!/bin/bash

SERVICE_NAME="capsule"
USER_NAME=$USER
# 获取当前脚本所在的绝对路径
WORK_DIR=$(pwd)
PYTHON_EXEC=$(which python3)

echo "--- 胶囊分配器 开机自启安装脚本 ---"
echo "工作目录: $WORK_DIR"
echo "执行用户: $USER_NAME"
echo "Python路径: $PYTHON_EXEC"

# 1. 创建 systemd 服务文件内容
SERVICE_CONTENT="[Unit]
Description=Smart Capsule Dispenser Service
After=network.target multi-user.target

[Service]
Type=simple
User=root
WorkingDirectory=$WORK_DIR
ExecStart=$PYTHON_EXEC $WORK_DIR/main_demo.py
Restart=always
RestartSec=5
# 确保输出即时刷新到日志
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target"

# 2. 写入系统目录 (需要 sudo 权限)
echo "正在创建服务文件 /etc/systemd/system/${SERVICE_NAME}.service ..."
echo "$SERVICE_CONTENT" | sudo tee /etc/systemd/system/${SERVICE_NAME}.service > /dev/null

# 3. 重新加载守护进程
echo "重新加载 systemd..."
sudo systemctl daemon-reload

# 4. 启用并启动服务
echo "启用开机自启..."
sudo systemctl enable $SERVICE_NAME

echo "正在尝试启动服务..."
sudo systemctl start $SERVICE_NAME

# 5. 检查状态
echo "--- 服务状态检查 ---"
sleep 2
if systemctl is-active --quiet $SERVICE_NAME; then
    echo "✅ 服务启动成功！"
    echo "你可以使用以下命令查看日志："
    echo "  sudo journalctl -u $SERVICE_NAME -f"
    echo ""
    echo "如果需要停止服务进行调试："
    echo "  sudo systemctl stop $SERVICE_NAME"
else
    echo "❌ 服务启动失败，请检查日志："
    echo "  sudo journalctl -u $SERVICE_NAME -n 20"
fi

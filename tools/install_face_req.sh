#!/bin/bash

echo "=== Raspberry Pi 5 人脸识别环境安装脚本 ==="
echo "⚠️  注意: 此过程可能需要 20-30 分钟，特别是编译 dlib 时。"

# 1. 更新系统并安装系统级依赖
echo "[1/4] 安装系统依赖..."
sudo apt-get update
sudo apt-get install -y build-essential cmake pkg-config libx11-dev libatlas-base-dev libgtk-3-dev libboost-python-dev python3-dev python3-pip python3-venv

# 2. 检查是否在虚拟环境中，如果没有则提示用户
# 在 Pi 5 Bookworm 上，强烈建议使用 venv
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  警告: 您当前不在 Python 虚拟环境中!"
    echo "建议先创建并激活虚拟环境，例如:"
    echo "  python3 -m venv venv"
    echo "  source venv/bin/activate"
    echo "是否继续直接安装? (y/n)"
    read -r response
    if [[ "$response" != "y" ]]; then
        exit 1
    fi
else
    echo "✅ 检测到虚拟环境: $VIRTUAL_ENV"
fi

# 3. 安装 Python 基础库
echo "[2/4] 安装 numpy..."
pip3 install numpy

# 4. 编译安装 dlib (最慢的一步)
echo "[3/4] 编译并安装 dlib (请耐心等待)..."
# 使用所有核心进行编译
pip3 install dlib

# 5. 安装 face_recognition 和 opencv
echo "[4/4] 安装 face_recognition 和 opencv..."
pip3 install face_recognition opencv-python-headless

echo "=== ✅ 安装完成! ==="
echo "您可以运行 'python3 face_enroll.py' 来测试人脸录入。"

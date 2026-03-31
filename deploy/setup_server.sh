#!/bin/bash
# 服务器一次性初始化脚本
# 运行方式：bash /opt/sensitive-word/deploy/setup_server.sh
set -e

echo "[setup] 创建目录..."
mkdir -p /opt/sensitive-word/data
mkdir -p /opt/sensitive-word/wordlist
mkdir -p /opt/sensitive-word/deploy

echo "[setup] 创建 Python 虚拟环境..."
cd /opt/sensitive-word
if [ ! -d "venv" ]; then
    python3.11 -m venv venv
    echo "[setup] venv 创建完成"
else
    echo "[setup] venv 已存在，跳过"
fi

echo "[setup] 初始化完成"

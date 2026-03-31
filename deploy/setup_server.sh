#!/bin/bash
# 服务器一次性初始化脚本
# 运行方式：bash /opt/sensitive-word/deploy/setup_server.sh [htpasswd_password]
# 第一个参数为 Basic Auth 密码，若不传则跳过 htpasswd 创建（后续手动创建）
set -e

HTPASSWD_PASS="${1:-}"

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

echo "[setup] 安装 nginx..."
if ! command -v nginx &>/dev/null; then
    apt-get update -q && apt-get install -y -q nginx apache2-utils
    echo "[setup] nginx 安装完成"
else
    echo "[setup] nginx 已存在，跳过"
fi

echo "[setup] 配置 nginx limit_req_zone..."
ZONE_LINE="limit_req_zone \$binary_remote_addr zone=sw_limit:10m rate=6r/m;"
NGINX_CONF="/etc/nginx/nginx.conf"
if ! grep -q "sw_limit" "$NGINX_CONF"; then
    # 插入到 http { 块第一行之后
    sed -i '/^http {/a \    '"$ZONE_LINE" "$NGINX_CONF"
    echo "[setup] limit_req_zone 已添加"
else
    echo "[setup] limit_req_zone 已存在，跳过"
fi

echo "[setup] 安装 nginx 站点配置..."
cp /opt/sensitive-word/deploy/nginx_sensitive.conf /etc/nginx/conf.d/sensitive-word.conf

if [ -n "$HTPASSWD_PASS" ]; then
    echo "[setup] 创建 Basic Auth 密码文件（用户名: admin）..."
    htpasswd -bc /etc/nginx/.htpasswd_sensitive admin "$HTPASSWD_PASS"
    echo "[setup] htpasswd 创建完成"
else
    echo "[setup] 未传入密码，跳过 htpasswd 创建"
    echo "        请手动执行：htpasswd -bc /etc/nginx/.htpasswd_sensitive admin <密码>"
fi

echo "[setup] 验证 nginx 配置..."
nginx -t

echo "[setup] 启动/重载 nginx..."
systemctl enable nginx
systemctl reload nginx || systemctl start nginx

echo "[setup] 初始化完成"

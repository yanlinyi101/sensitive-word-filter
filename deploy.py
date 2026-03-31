"""
deploy.py — 一键部署敏感词工具到腾讯云

首次部署：python3 deploy.py --first
后续部署：python3 deploy.py
"""

import os
import subprocess
import sys
import tarfile
import tempfile
import argparse

SSH_KEY    = "/Users/xxx/Projects/AI客服/wx-ai-customer-service/deploy/zm_mac.pem"
SSH_HOST   = "root@118.25.104.84"
REMOTE_DIR = "/opt/sensitive-word"
SERVICE    = "sensitive-word"
LOCAL_ROOT = os.path.dirname(os.path.abspath(__file__))

DEPLOY_DIRS  = ["app", "static", "scripts"]
DEPLOY_FILES = ["requirements.txt"]


def run(cmd: str, desc: str) -> str:
    print(f"  {desc} ...")
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        print(f"  [失败]\n{r.stderr.strip()}")
        sys.exit(1)
    return r.stdout.strip()


def build_tar(include_wordlist: bool = False) -> str:
    tmp = tempfile.mktemp(suffix=".tar.gz")
    with tarfile.open(tmp, "w:gz") as tar:
        for d in DEPLOY_DIRS:
            path = os.path.join(LOCAL_ROOT, d)
            if os.path.exists(path):
                tar.add(path, arcname=d)
                print(f"    + {d}/")
        for f in DEPLOY_FILES:
            path = os.path.join(LOCAL_ROOT, f)
            if os.path.exists(path):
                tar.add(path, arcname=f)
                print(f"    + {f}")
        if include_wordlist:
            wl = os.path.join(LOCAL_ROOT, "wordlist", "houbb_base.txt")
            if os.path.exists(wl):
                tar.add(wl, arcname="wordlist/houbb_base.txt")
                print(f"    + wordlist/houbb_base.txt (~3MB，首次上传)")
    size_mb = os.path.getsize(tmp) / 1024 / 1024
    print(f"  打包完成：{size_mb:.1f} MB")
    return tmp


def main():
    parser = argparse.ArgumentParser(description="敏感词工具部署脚本")
    parser.add_argument("--first", action="store_true",
                        help="首次部署：上传词表、安装依赖、注册并启动服务")
    args = parser.parse_args()

    print("[1/3] 打包文件")
    tar = build_tar(include_wordlist=args.first)

    if args.first:
        print("\n[prep] 上传 deploy/ 配置文件...")
        deploy_dir = os.path.join(LOCAL_ROOT, "deploy")
        run(
            f'ssh -i "{SSH_KEY}" -o StrictHostKeyChecking=no {SSH_HOST} "mkdir -p {REMOTE_DIR}"',
            "创建远程目录"
        )
        run(
            f'scp -i "{SSH_KEY}" -o StrictHostKeyChecking=no -r "{deploy_dir}" {SSH_HOST}:{REMOTE_DIR}/deploy',
            "上传 deploy/ 目录"
        )

    print("\n[2/3] 上传代码包")
    run(
        f'scp -i "{SSH_KEY}" -o StrictHostKeyChecking=no "{tar}" {SSH_HOST}:/tmp/deploy.tar.gz',
        "scp 上传"
    )

    print("\n[3/3] 解压并重启服务")
    if args.first:
        remote_cmd = " && ".join([
            f"bash {REMOTE_DIR}/deploy/setup_server.sh",
            f"tar -xzf /tmp/deploy.tar.gz -C {REMOTE_DIR}",
            f"rm /tmp/deploy.tar.gz",
            f"cd {REMOTE_DIR} && venv/bin/pip install -q -r requirements.txt",
            f"cp {REMOTE_DIR}/deploy/sensitive-word.service /etc/systemd/system/",
            f"mkdir -p {REMOTE_DIR}/data",
            f"systemctl daemon-reload",
            f"systemctl enable {SERVICE}",
            f"systemctl start {SERVICE}",
            f"sleep 2",
            f"systemctl is-active {SERVICE}",
        ])
    else:
        remote_cmd = " && ".join([
            f"tar -xzf /tmp/deploy.tar.gz -C {REMOTE_DIR}",
            f"rm /tmp/deploy.tar.gz",
            f"systemctl restart {SERVICE}",
            f"sleep 2",
            f"systemctl is-active {SERVICE}",
        ])

    ssh_cmd = f'ssh -i "{SSH_KEY}" -o StrictHostKeyChecking=no {SSH_HOST} \'{remote_cmd}\''
    output = run(ssh_cmd, "解压 & 重启")
    print(f"  服务状态：{output}")

    os.unlink(tar)
    print("\n✅ 部署完成！")

    if args.first:
        print("""
后续步骤：

1. 确认腾讯云安全组已放行 TCP 8001（如未操作请登录控制台添加）

2. 确认 .env 已创建（若未创建请执行）：
   ssh -i "{key}" {host}
   cat > /opt/sensitive-word/.env << 'EOF'
   GEMINI_API_KEY=你的密钥
   DATABASE_URL=sqlite:////opt/sensitive-word/data/app.db
   EOF
   systemctl restart sensitive-word

3. 导入词库（约 65000 条，需等待约 30 秒）：
   ssh -i "{key}" {host} \\
     'cd /opt/sensitive-word && venv/bin/python -m app.db.seed'

4. 访问：http://118.25.104.84:8001
""".format(key=SSH_KEY, host=SSH_HOST))


if __name__ == "__main__":
    main()

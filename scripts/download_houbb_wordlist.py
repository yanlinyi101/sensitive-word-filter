"""
下载 houbb/sensitive-word 词表并转换为项目格式。

输出格式：word,category,risk_level（每行一条）
风险等级默认为 2（中风险），分类为"通用"。
用户可在前端词库管理页面调整单个词条。

用法：
    python scripts/download_houbb_wordlist.py
    python scripts/download_houbb_wordlist.py --output wordlist/houbb_base.txt --risk 2
"""

import argparse
import sys
import urllib.request
import urllib.error

DICT_URL = (
    "https://raw.githubusercontent.com/houbb/sensitive-word/master/"
    "src/test/resources/dict_v20240407.txt"
)

DEFAULT_CATEGORY = "通用"
DEFAULT_RISK_LEVEL = 2


def download(url: str) -> list[str]:
    print(f"正在下载: {url}")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
    except urllib.error.URLError as e:
        print(f"下载失败: {e}", file=sys.stderr)
        sys.exit(1)

    lines = [line.strip() for line in raw.splitlines()]
    words = [w for w in lines if w and not w.startswith("#")]
    print(f"下载完成，共 {len(words)} 个词条")
    return words


def convert(words: list[str], category: str, risk_level: int) -> list[str]:
    """转换为 word,category,risk_level 格式，去重。"""
    seen: set[str] = set()
    rows: list[str] = []
    for word in words:
        if word in seen:
            continue
        seen.add(word)
        # 词条本身不能含英文逗号（逗号会破坏 CSV 格式），跳过
        if "," in word:
            continue
        rows.append(f"{word},{category},{risk_level}")
    return rows


def write_output(rows: list[str], output_path: str, append: bool) -> None:
    mode = "a" if append else "w"
    action = "追加" if append else "写入"
    with open(output_path, mode, encoding="utf-8") as f:
        for row in rows:
            f.write(row + "\n")
    print(f"{action}完成 → {output_path}（{len(rows)} 条）")


def main() -> None:
    parser = argparse.ArgumentParser(description="下载 houbb/sensitive-word 词表")
    parser.add_argument(
        "--output",
        default="wordlist/houbb_base.txt",
        help="输出文件路径（默认：wordlist/houbb_base.txt）",
    )
    parser.add_argument(
        "--category",
        default=DEFAULT_CATEGORY,
        help=f"默认分类（默认：{DEFAULT_CATEGORY}）",
    )
    parser.add_argument(
        "--risk",
        type=int,
        choices=[1, 2, 3],
        default=DEFAULT_RISK_LEVEL,
        help=f"默认风险等级 1/2/3（默认：{DEFAULT_RISK_LEVEL}）",
    )
    parser.add_argument(
        "--append",
        action="store_true",
        help="追加到已有文件而不是覆盖",
    )
    args = parser.parse_args()

    words = download(DICT_URL)
    rows = convert(words, args.category, args.risk)

    skipped = len(words) - len(rows)
    if skipped:
        print(f"跳过含逗号词条 {skipped} 个")

    write_output(rows, args.output, args.append)
    print("\n完成。可运行以下命令将词库导入数据库：")
    print("    python -m app.db.seed")


if __name__ == "__main__":
    main()

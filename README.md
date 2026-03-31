# 逐字稿风险审查工具

针对视频逐字稿（直播口播稿、纪录片剧本）的风险审查与改写工具。通过**词库匹配 + 规则引擎 + Gemini LLM** 三层机制，自动标注低/中/高风险句，并提供改写建议。

## 功能特性

- **三层风险检测**：DFA 词库匹配 → 规则引擎（只升不降）→ Gemini LLM 上下文复核（可降级）
- **句级标注**：每句独立输出风险等级（低/中/高）+ 命中词 + 触发规则 + 改写建议
- **可管理词库**：支持在线增删改词条、启用/禁用、按分类筛选
- **可配置规则**：支持 `word_match` / `category_count` / `regex` 三类条件，AND/OR 组合
- **历史记录**：保存每次审查结果，支持回溯查看

## 截图

> 审查结果页——句子按风险等级红/橙/黄高亮，右侧展示命中词与 LLM 改写建议

## 快速开始

```bash
pip install -r requirements.txt
cp .env.example .env  # 填写 GEMINI_API_KEY
uvicorn app.main:app --reload
```

访问 http://localhost:8000

## 词库更新

默认词库来自 [houbb/sensitive-word](https://github.com/houbb/sensitive-word)，可用脚本一键下载最新版：

```bash
python3 scripts/download_houbb_wordlist.py
python3 -m app.db.seed
```

## 规则引擎

支持三类条件，可在「规则管理」页面配置：

```json
{
  "conditions": [
    {"type": "word_match", "words": ["根治", "特效"], "op": "any"},
    {"type": "category_count", "category": "功效词", "min": 2},
    {"type": "regex", "pattern": "\\d+%.*效果"}
  ],
  "logic": "AND"
}
```

## 运行测试

```bash
pytest
```

## 环境变量

| 变量 | 说明 | 默认值 |
|---|---|---|
| `GEMINI_API_KEY` | Gemini API 密钥（LLM 复核必填） | 无 |
| `DATABASE_URL` | SQLite 数据库路径 | `sqlite:///./app.db` |

## 技术栈

| 层 | 技术 |
|---|---|
| 后端 | Python 3.11 + FastAPI + SQLAlchemy |
| DFA 匹配 | [pyahocorasick](https://github.com/WojciechMula/pyahocorasick) |
| LLM | Google Gemini API (`google-generativeai`) |
| 数据库 | SQLite |
| 前端 | HTML + [Alpine.js](https://alpinejs.dev/) |

## 引用的开源项目

| 项目 | 用途 | 许可证 |
|---|---|---|
| [houbb/sensitive-word](https://github.com/houbb/sensitive-word) | 中文敏感词词库来源，项目提供 65,000+ 词条，本项目通过脚本下载其测试资源中的词表文件 | Apache-2.0 |
| [WojciechMula/pyahocorasick](https://github.com/WojciechMula/pyahocorasick) | Aho-Corasick 多模式字符串匹配算法（DFA 引擎），用于高效词库匹配 | BSD-3-Clause |
| [tiangolo/fastapi](https://github.com/tiangolo/fastapi) | Python Web 框架，提供 API 层与依赖注入 | MIT |
| [alpinejs/alpine](https://github.com/alpinejs/alpine) | 轻量前端框架，用于单页交互 | MIT |

## 免责声明

本项目词库数据来源于 [houbb/sensitive-word](https://github.com/houbb/sensitive-word)，词表版权归原项目所有。本工具仅用于内容风险辅助审查，最终判断以人工复核为准。

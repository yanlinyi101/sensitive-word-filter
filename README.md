# 逐字稿风险审查工具

针对视频逐字稿（直播口播稿、纪录片剧本）的风险审查与改写工具。通过词库匹配 + 规则引擎 + Gemini LLM 三层机制，自动标注低/中/高风险句，并提供改写建议。

## 启动

```bash
pip install -r requirements.txt
cp .env.example .env  # 填写 GEMINI_API_KEY
uvicorn app.main:app --reload
```

访问 http://localhost:8000

## 首次运行

启动时自动从 `wordlist/houbb_base.txt` 导入基础词库。如需更新词库文件后重新导入：

```bash
python -m app.db.seed
```

## 词库格式

`wordlist/houbb_base.txt` 每行一条：

```
word,category,risk_level
```

- `category`：医疗、广告法、政治、版权等
- `risk_level`：1=低 2=中 3=高

## 规则引擎

支持三类条件（可在"规则管理"页面配置）：

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

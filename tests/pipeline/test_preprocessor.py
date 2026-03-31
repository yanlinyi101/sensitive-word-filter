from app.pipeline.preprocessor import preprocess

def test_splits_on_chinese_punctuation():
    result = preprocess("你好。这是测试。再见。")
    assert result == ["你好", "这是测试", "再见"]

def test_splits_on_newline():
    result = preprocess("第一句\n第二句")
    assert result == ["第一句", "第二句"]

def test_removes_timestamp():
    result = preprocess("[00:01:23] 主播说的话。")
    assert result == ["主播说的话"]

def test_removes_speaker_label():
    result = preprocess("主播A：这是内容。")
    assert result == ["这是内容"]

def test_skips_empty():
    result = preprocess("有效句子。\n\n另一句。")
    assert result == ["有效句子", "另一句"]

def test_mixed_punctuation():
    result = preprocess("这个产品很好！真的吗？是的。")
    assert result == ["这个产品很好", "真的吗", "是的"]

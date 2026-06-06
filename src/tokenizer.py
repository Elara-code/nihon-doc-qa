"""BM25 用的中日友好分词。

为什么不直接按空格切？日文 / 中文没有词边界空格，按空格切等于不切。
没有 MeCab/jieba 也能稳定工作的折中方案：

- ASCII 字母数字串整体保留（如 ``inv-002``、``t_stock``、``tls``），
  这正是 BM25 相对向量检索的强项——型号 / 表名 / 缩写的精确字面匹配。
- 同时把 ``inv-002`` 拆出 ``inv`` / ``002`` 子词，兼顾召回。
- CJK 字符用 **bigram（二元组）**，让"在庫""引当"这类词能被匹配，
  单字也保留，应对单字查询。

只要 query 和 document 用同一套分词，BM25 的匹配就成立。
"""
from __future__ import annotations

import re

_ASCII_TOKEN = re.compile(r"[a-z0-9]+(?:[-_][a-z0-9]+)*")
_CJK_CHAR = re.compile(r"[぀-ヿ㐀-䶿一-鿿]")


def tokenize(text: str) -> list[str]:
    if not text:
        return []
    lowered = text.lower()
    tokens: list[str] = []

    # ASCII 字母数字（含连字符/下划线的型号、表名）
    for tok in _ASCII_TOKEN.findall(lowered):
        tokens.append(tok)
        # 拆分子词，兼顾召回（inv-002 -> inv, 002）
        parts = re.split(r"[-_]", tok)
        if len(parts) > 1:
            tokens.extend(p for p in parts if p)

    # CJK：bigram + unigram
    cjk_chars = _CJK_CHAR.findall(text)
    for i in range(len(cjk_chars) - 1):
        tokens.append(cjk_chars[i] + cjk_chars[i + 1])
    tokens.extend(cjk_chars)  # 单字，应对单字查询

    return tokens

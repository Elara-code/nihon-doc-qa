"""中日文本规整与语言识别。

针对对日技术文档（日文 / 中日混排）的常见坑：

1. 全角/半角混用：日文 PDF 里数字、英文、括号常是全角，NFKC 归一化统一成半角，
   既利于检索匹配（"INV-001" vs "ＩＮＶ－００１"），也方便阅读。
2. 字符间杂散空格：部分日文 PDF 在每个假名/汉字之间插空格，清掉 CJK 之间的空格。
3. 提取乱码：字体缺 ToUnicode 映射时 PyMuPDF 会吐出乱码/替换字符，做个启发式检测并告警。
"""
from __future__ import annotations

import re
import unicodedata

# CJK 统一表意文字 + 日文假名 + 常用标点
_CJK_PATTERN = re.compile(
    r"[぀-ヿ㐀-䶿一-鿿豈-﫿ｦ-ﾟ]"
)
# 两个 CJK 字符之间的空白（日文 PDF 常见的杂散空格）
_CJK_SPACE_CJK = re.compile(
    r"(?<=[぀-ヿ㐀-䶿一-鿿])[ \t]+(?=[぀-ヿ㐀-䶿一-鿿])"
)
# 控制字符与 Unicode 替换字符（乱码信号）
_GARBLED_PATTERN = re.compile(r"[�\x00-\x08\x0b\x0c\x0e-\x1f]")


def normalize_text(text: str) -> str:
    """对提取出的文本做规整：NFKC + 清理 CJK 间杂散空格 + 压缩多余空行。"""
    if not text:
        return ""
    # NFKC：全角→半角、兼容字符归一
    text = unicodedata.normalize("NFKC", text)
    # 清掉 CJK 字符之间的杂散空格
    text = _CJK_SPACE_CJK.sub("", text)
    # 行内多个空格压成一个
    text = re.sub(r"[ \t]{2,}", " ", text)
    # 连续 3+ 空行压成 2 个
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def cjk_ratio(text: str) -> float:
    """CJK 字符占非空白字符的比例。用于判断是否含中日内容。"""
    stripped = re.sub(r"\s", "", text)
    if not stripped:
        return 0.0
    return len(_CJK_PATTERN.findall(text)) / len(stripped)


def looks_garbled(text: str, threshold: float = 0.02) -> bool:
    """启发式判断提取是否乱码：替换字符/控制字符占比超过阈值即认为可疑。"""
    if not text:
        return False
    bad = len(_GARBLED_PATTERN.findall(text))
    return bad / max(len(text), 1) > threshold


def detect_language(text: str) -> str:
    """粗粒度语言识别，返回 'ja' / 'zh' / 'other'。

    依据：含平假名/片假名 → 日文；只有汉字无假名 → 中文；否则 other。
    用于让回答语言自动适配提问语言。
    """
    has_kana = bool(re.search(r"[぀-ゟ゠-ヿ]", text))
    has_han = bool(re.search(r"[一-鿿]", text))
    if has_kana:
        return "ja"
    if has_han:
        return "zh"
    return "other"

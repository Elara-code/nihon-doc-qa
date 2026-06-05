"""Day 6 验收脚本：中日混排文本规整与语言识别。

不依赖外部库，可直接运行验证 src/text_utils.py 的行为。

用法：
    python scripts/test_jp_text.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.text_utils import (
    cjk_ratio,
    detect_language,
    looks_garbled,
    normalize_text,
)


def main() -> None:
    cases = [
        # 全角数字/英文/括号 → NFKC 归一为半角
        ("全角归一", "商品コード（ＩＮＶ－００１）の在庫数", ),
        # 日文 PDF 常见：假名/汉字之间被插入空格
        ("清杂散空格", "在 庫 管 理 シ ス テ ム"),
        # 中日混排
        ("中日混排", "引当 (ひきあて)：受注に対して在庫を確保する処理。中文称为分配。"),
    ]
    print("===== normalize_text =====")
    for name, raw in cases:
        print(f"[{name}]")
        print(f"  before: {raw!r}")
        print(f"  after : {normalize_text(raw)!r}")
        print()

    print("===== detect_language =====")
    samples = [
        "出庫登録の引当方式は何ですか？",   # ja（含假名）
        "T_STOCK 的主键是什么？",          # zh
        "INV-001",                         # other
    ]
    for s in samples:
        print(f"  {detect_language(s):5s} <- {s}")

    print("\n===== cjk_ratio / looks_garbled =====")
    print(f"  cjk_ratio('在庫管理 system'): {cjk_ratio('在庫管理 system'):.2f}")
    clean = "正常な日本語テキスト"
    garbled = "���\x01\x02乱码"
    print(f"  looks_garbled(正常文本): {looks_garbled(clean)}")
    print(f"  looks_garbled(含替换字符/控制字符): {looks_garbled(garbled)}")


if __name__ == "__main__":
    main()

"""Day 2 验收脚本：解析文档 → 切块 → 打印结果。

用法：
    python scripts/test_chunking.py samples/sample_spec.txt
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.config import settings
from src.loader import load_and_chunk


def main() -> None:
    if len(sys.argv) < 2:
        files = [Path(__file__).resolve().parents[1] / "samples" / "sample_spec.txt"]
    else:
        files = [Path(p) for p in sys.argv[1:]]

    chunks = load_and_chunk(files, settings.chunk_size, settings.chunk_overlap)
    print(f"共切出 {len(chunks)} 个 chunk（chunk_size={settings.chunk_size}, overlap={settings.chunk_overlap}）\n")
    for c in chunks[:5]:
        print(f"--- [{c.chunk_id}] {c.source} p.{c.page} ({len(c.text)} chars) ---")
        print(c.text)
        print()
    if len(chunks) > 5:
        print(f"... 还有 {len(chunks) - 5} 个未显示")


if __name__ == "__main__":
    main()

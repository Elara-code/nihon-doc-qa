"""Day 4 验收脚本：朴素 RAG 全链路。

流程：入库样例文档 → 提问 → 检索 → 拼 prompt → 大模型回答。

用法：
    python scripts/test_rag.py
    python scripts/test_rag.py "在庫照会の応答時間の要件は？"
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.pipeline import RagPipeline


SAMPLE_QUESTIONS = [
    "出庫登録の引当処理は何方式ですか？",
    "T_STOCK 的主键是什么？",
    "在庫照会の応答時間の SLA は？",
]


def main() -> None:
    sample = Path(__file__).resolve().parents[1] / "samples" / "sample_spec.txt"
    pipeline = RagPipeline()
    n = pipeline.ingest([sample], reset=True)
    print(f"[ingest] {sample.name} -> {n} chunks 入库\n")

    queries = sys.argv[1:] if len(sys.argv) > 1 else SAMPLE_QUESTIONS
    for q in queries:
        print(f"========== Q: {q} ==========")
        result = pipeline.answer(q)
        print(f"A: {result['answer']}\n")
        print("引用来源：")
        for s in result["sources"]:
            print(f"  - {s['source']} p.{s['page']} (dist={s['distance']:.4f})")
        print()


if __name__ == "__main__":
    main()

"""Day 11-12 验收脚本：对比纯向量 vs 混合检索。

重点看型号/编号、表名这类问题——混合检索（BM25）应该比纯向量召回得更准。

用法：
    python scripts/test_hybrid.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.config import settings
from src.embedding import Embedder
from src.loader import load_and_chunk
from src.retriever import HybridRetriever
from src.vectorstore import VectorStore

# 偏向 BM25 强项的问题：型号 / 表名 / 缩写
PROBE_QUERIES = [
    "入库登记功能的编号 INV-002",
    "T_STOCK 的主键",
    "TLS 版本要求",
]


def show(title: str, hits: list[dict]) -> None:
    print(f"  [{title}]")
    for i, h in enumerate(hits, 1):
        meta = h["metadata"]
        tag = f"p.{meta.get('page')}"
        snippet = h["text"][:50].replace("\n", " ")
        print(f"    {i}. ({tag}) {snippet}…")


def main() -> None:
    sample = Path(__file__).resolve().parents[1] / "samples" / "sample_spec.txt"
    embedder = Embedder()
    store = VectorStore()
    store.reset()
    chunks = load_and_chunk([sample], settings.chunk_size, settings.chunk_overlap)
    store.add(chunks, embedder.embed([c.text for c in chunks]))
    print(f"[ingest] {sample.name} -> {len(chunks)} chunks\n")

    vec_r = HybridRetriever(embedder, store, mode="vector")
    hyb_r = HybridRetriever(embedder, store, mode="hybrid")

    for q in PROBE_QUERIES:
        print(f"========== Q: {q} ==========")
        show("纯向量", vec_r.retrieve(q, top_k=3))
        show("混合检索", hyb_r.retrieve(q, top_k=3))
        print()


if __name__ == "__main__":
    main()

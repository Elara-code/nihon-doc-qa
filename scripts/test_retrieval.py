"""Day 3 验收脚本：把样例文档向量化入库，并做一次检索。

用法：
    python scripts/test_retrieval.py
    python scripts/test_retrieval.py "出庫の引当方式は？"
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.config import settings
from src.embedding import Embedder
from src.loader import load_and_chunk
from src.retriever import Retriever
from src.vectorstore import VectorStore


def main() -> None:
    sample = Path(__file__).resolve().parents[1] / "samples" / "sample_spec.txt"
    chunks = load_and_chunk([sample], settings.chunk_size, settings.chunk_overlap)
    print(f"[ingest] {sample.name} -> {len(chunks)} chunks")

    embedder = Embedder()
    store = VectorStore()
    store.reset()  # 每次重新入库，避免重复
    vectors = embedder.embed([c.text for c in chunks])
    store.add(chunks, vectors)
    print(f"[ingest] 入库完成，集合 chunk 数：{store.count()}")

    retriever = Retriever(embedder=embedder, store=store)
    query = sys.argv[1] if len(sys.argv) > 1 else "出庫登録の引当方式は何ですか？"
    print(f"\n[query] {query}\n")
    hits = retriever.retrieve(query, top_k=3)
    for i, hit in enumerate(hits, 1):
        meta = hit["metadata"]
        print(f"--- Top {i} | {meta['source']} p.{meta['page']} | dist={hit['distance']:.4f} ---")
        print(hit["text"][:200])
        print()


if __name__ == "__main__":
    main()

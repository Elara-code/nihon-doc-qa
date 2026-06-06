"""BM25 关键词检索索引。

补向量检索的短板：型号（INV-002）、表名（T_STOCK）、缩写（TLS）这类
"语义相近但字面必须精确匹配"的词，BM25 比向量更可靠。

索引直接从向量库的全部 chunk 重建，二者共用同一份数据，避免双重持久化。
"""
from __future__ import annotations

from rank_bm25 import BM25Okapi

from src.tokenizer import tokenize


class BM25Index:
    def __init__(self, records: list[dict]) -> None:
        """records: [{'id','text','metadata'}, ...]，通常来自 VectorStore.get_all()。"""
        self.records = records
        self._corpus_tokens = [tokenize(r["text"]) for r in records]
        self._bm25 = BM25Okapi(self._corpus_tokens) if records else None

    @classmethod
    def from_store(cls, store) -> "BM25Index":
        return cls(store.get_all())

    def search(self, query: str, top_k: int) -> list[dict]:
        if not self._bm25:
            return []
        scores = self._bm25.get_scores(tokenize(query))
        ranked = sorted(
            range(len(scores)), key=lambda i: scores[i], reverse=True
        )[:top_k]
        hits: list[dict] = []
        for rank, i in enumerate(ranked):
            if scores[i] <= 0:
                continue
            r = self.records[i]
            hits.append(
                {
                    "id": r["id"],
                    "text": r["text"],
                    "metadata": r["metadata"],
                    "bm25_score": float(scores[i]),
                }
            )
        return hits

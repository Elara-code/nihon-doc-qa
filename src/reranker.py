"""重排序（Rerank）。

混合检索给出的候选里，相关度排序并不总准。交叉编码器（cross-encoder）
把 query 和每个候选拼在一起联合编码打分，比"分别编码再算相似度"的
双塔向量精确得多，但更慢——所以只用它对少量候选做二次精排。

默认 BAAI/bge-reranker-v2-m3，支持中日多语言。模型惰性加载。
"""
from __future__ import annotations

from sentence_transformers import CrossEncoder

from src.config import settings


class Reranker:
    def __init__(self, model_name: str | None = None) -> None:
        self.model_name = model_name or settings.rerank_model
        self._model: CrossEncoder | None = None

    @property
    def model(self) -> CrossEncoder:
        if self._model is None:
            self._model = CrossEncoder(self.model_name)
        return self._model

    def rerank(self, query: str, hits: list[dict], top_k: int) -> list[dict]:
        if not hits:
            return []
        pairs = [(query, h["text"]) for h in hits]
        scores = self.model.predict(pairs)
        for h, s in zip(hits, scores):
            h["rerank_score"] = float(s)
        hits.sort(key=lambda h: h["rerank_score"], reverse=True)
        return hits[:top_k]

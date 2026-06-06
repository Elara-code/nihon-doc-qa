"""检索器。

- Retriever：仅向量检索（Week 1 朴素版，保留作为对比基线）。
- HybridRetriever：向量 + BM25 的 RRF 融合（Week 3 Day 11-12）。
  通过 settings.retrieval_mode 控制：vector / hybrid。
"""
from __future__ import annotations

from src.bm25_index import BM25Index
from src.config import settings
from src.embedding import Embedder
from src.vectorstore import VectorStore


class Retriever:
    """仅向量检索（基线）。"""

    def __init__(
        self,
        embedder: Embedder | None = None,
        store: VectorStore | None = None,
    ) -> None:
        self.embedder = embedder or Embedder()
        self.store = store or VectorStore()

    def retrieve(self, query: str, top_k: int | None = None) -> list[dict]:
        k = top_k or settings.top_k
        vec = self.embedder.embed([query])[0]
        return self.store.search(vec, k)


def reciprocal_rank_fusion(
    ranked_lists: list[list[dict]],
    rrf_k: int,
) -> list[dict]:
    """RRF 融合多路检索结果。

    每个候选的分数 = Σ 1/(rrf_k + 该路内排名)。
    只看排名不看原始分数，天然解决"向量距离"和"BM25 分"量纲不可比的问题。
    """
    scores: dict[str, float] = {}
    merged: dict[str, dict] = {}
    for ranked in ranked_lists:
        for rank, hit in enumerate(ranked):
            hid = hit["id"]
            scores[hid] = scores.get(hid, 0.0) + 1.0 / (rrf_k + rank)
            # 保留首次见到的命中内容，合并各路分数字段
            if hid not in merged:
                merged[hid] = dict(hit)
            else:
                merged[hid].update({k: v for k, v in hit.items() if k not in merged[hid]})
    fused = []
    for hid, score in sorted(scores.items(), key=lambda kv: kv[1], reverse=True):
        item = merged[hid]
        item["rrf_score"] = score
        fused.append(item)
    return fused


class HybridRetriever:
    """向量 + BM25 混合检索（RRF 融合）。"""

    def __init__(
        self,
        embedder: Embedder | None = None,
        store: VectorStore | None = None,
        mode: str | None = None,
    ) -> None:
        self.embedder = embedder or Embedder()
        self.store = store or VectorStore()
        self.mode = mode or settings.retrieval_mode
        self._bm25: BM25Index | None = None

    @property
    def bm25(self) -> BM25Index:
        if self._bm25 is None:
            self._bm25 = BM25Index.from_store(self.store)
        return self._bm25

    def refresh(self) -> None:
        """入库后调用，丢弃缓存的 BM25 索引以便下次按新数据重建。"""
        self._bm25 = None

    def retrieve(self, query: str, top_k: int | None = None) -> list[dict]:
        k = top_k or settings.top_k

        if self.mode == "vector":
            vec = self.embedder.embed([query])[0]
            return self.store.search(vec, k)

        # hybrid：向量 + BM25 两路各召回 candidate_k 个候选，再 RRF 融合
        cand = settings.candidate_k
        vec = self.embedder.embed([query])[0]
        vector_hits = self.store.search(vec, cand)
        bm25_hits = self.bm25.search(query, cand)
        fused = reciprocal_rank_fusion([vector_hits, bm25_hits], settings.rrf_k)
        return fused[:k]

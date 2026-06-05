"""检索器：把 Embedder 和 VectorStore 串起来。"""
from __future__ import annotations

from src.config import settings
from src.embedding import Embedder
from src.vectorstore import VectorStore


class Retriever:
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

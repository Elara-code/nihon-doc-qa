"""RAG 流程编排：ingest（入库）+ answer（问答）。"""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

from src.config import settings
from src.embedding import Embedder
from src.generator import Generator
from src.loader import load_and_chunk
from src.retriever import Retriever
from src.vectorstore import VectorStore


class RagPipeline:
    def __init__(self) -> None:
        self.embedder = Embedder()
        self.store = VectorStore()
        self.retriever = Retriever(self.embedder, self.store)
        self._generator: Generator | None = None  # 惰性初始化，避免缺 key 时阻塞

    @property
    def generator(self) -> Generator:
        if self._generator is None:
            self._generator = Generator()
        return self._generator

    def ingest(self, paths: Iterable[str | Path], reset: bool = False) -> int:
        if reset:
            self.store.reset()
        chunks = load_and_chunk(paths, settings.chunk_size, settings.chunk_overlap)
        vectors = self.embedder.embed([c.text for c in chunks])
        self.store.add(chunks, vectors)
        return len(chunks)

    def answer(self, query: str, top_k: int | None = None) -> dict:
        hits = self.retriever.retrieve(query, top_k=top_k)
        answer = self.generator.generate(query, hits)
        sources = [
            {
                "source": h["metadata"].get("source"),
                "page": h["metadata"].get("page"),
                "distance": h.get("distance"),
            }
            for h in hits
        ]
        return {"answer": answer, "sources": sources, "hits": hits}

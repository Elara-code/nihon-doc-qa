"""Chroma 向量库的薄封装。

设计取舍：
- 直接传入预计算好的 embedding，不依赖 Chroma 自带的 embedding function，
  这样 embedding 模型的选择和持久化的向量库解耦。
- 用 cosine 距离（与 bge 系列归一化向量相符）。
"""
from __future__ import annotations

from typing import Sequence

import chromadb
from chromadb.config import Settings as ChromaSettings

from src.config import settings
from src.loader import Chunk


class VectorStore:
    def __init__(
        self,
        persist_dir: str | None = None,
        collection_name: str | None = None,
    ) -> None:
        self.persist_dir = persist_dir or settings.chroma_dir
        self.collection_name = collection_name or settings.chroma_collection
        self.client = chromadb.PersistentClient(
            path=self.persist_dir,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def add(self, chunks: Sequence[Chunk], embeddings: Sequence[Sequence[float]]) -> None:
        if not chunks:
            return
        ids = [f"{c.source}:{c.page}:{c.chunk_id}" for c in chunks]
        self.collection.add(
            ids=ids,
            documents=[c.text for c in chunks],
            embeddings=[list(v) for v in embeddings],
            metadatas=[c.to_metadata() for c in chunks],
        )

    def search(
        self,
        query_embedding: Sequence[float],
        top_k: int,
    ) -> list[dict]:
        result = self.collection.query(
            query_embeddings=[list(query_embedding)],
            n_results=top_k,
        )
        hits: list[dict] = []
        docs = result.get("documents", [[]])[0]
        metas = result.get("metadatas", [[]])[0]
        dists = result.get("distances", [[]])[0]
        for text, meta, dist in zip(docs, metas, dists):
            hits.append({"text": text, "metadata": meta, "distance": dist})
        return hits

    def count(self) -> int:
        return self.collection.count()

    def reset(self) -> None:
        """删除集合并重建（演示/测试用）。"""
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
        )

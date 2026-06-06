"""Embedding 封装。

默认使用 BAAI/bge-m3，支持中日多语言。模型加载是惰性的，
首次调用时才下载/装载，避免 import 时阻塞。
"""
from __future__ import annotations

from typing import Sequence

from sentence_transformers import SentenceTransformer

from src.config import settings


class Embedder:
    def __init__(self, model_name: str | None = None) -> None:
        self.model_name = model_name or settings.embedding_model
        self._model: SentenceTransformer | None = None

    @property
    def model(self) -> SentenceTransformer:
        if self._model is None:
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        if not texts:
            return []
        vectors = self.model.encode(
            list(texts),
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return vectors.tolist()

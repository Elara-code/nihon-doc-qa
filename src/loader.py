"""文档解析与切块。

- PDF 走 PyMuPDF (fitz)，按页提取文本，并保留页码。
- 同时支持 .txt 方便没有 PDF 时也能跑通链路。
- 切块策略：固定窗口 + 重叠，按字符数滑动；对中日文档比按 token 更直观。
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import fitz  # PyMuPDF


@dataclass
class Chunk:
    text: str
    source: str   # 文件名
    page: int     # 1-based 页码；txt 文件统一记为 1
    chunk_id: int

    def to_metadata(self) -> dict:
        return {"source": self.source, "page": self.page, "chunk_id": self.chunk_id}


def _read_pdf_pages(path: Path) -> list[tuple[int, str]]:
    pages: list[tuple[int, str]] = []
    with fitz.open(path) as doc:
        for i, page in enumerate(doc, start=1):
            text = page.get_text("text") or ""
            pages.append((i, text))
    return pages


def _read_txt_pages(path: Path) -> list[tuple[int, str]]:
    return [(1, path.read_text(encoding="utf-8"))]


def read_document(path: str | Path) -> list[tuple[int, str]]:
    """返回 [(page_number, page_text), ...]。"""
    p = Path(path)
    suffix = p.suffix.lower()
    if suffix == ".pdf":
        return _read_pdf_pages(p)
    if suffix in {".txt", ".md"}:
        return _read_txt_pages(p)
    raise ValueError(f"暂不支持的文件类型: {suffix}")


def chunk_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    """按字符滑窗切块。空白会被压缩，方便阅读检查。"""
    text = text.strip()
    if not text:
        return []
    if chunk_size <= 0:
        raise ValueError("chunk_size 必须为正整数")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap 应在 [0, chunk_size) 区间")

    chunks: list[str] = []
    step = chunk_size - overlap
    for start in range(0, len(text), step):
        piece = text[start : start + chunk_size].strip()
        if piece:
            chunks.append(piece)
        if start + chunk_size >= len(text):
            break
    return chunks


def load_and_chunk(
    paths: Iterable[str | Path],
    chunk_size: int,
    overlap: int,
) -> list[Chunk]:
    """读多个文档并切块；返回带页码/来源元数据的 Chunk 列表。"""
    all_chunks: list[Chunk] = []
    global_id = 0
    for path in paths:
        p = Path(path)
        for page_no, page_text in read_document(p):
            for piece in chunk_text(page_text, chunk_size, overlap):
                all_chunks.append(
                    Chunk(text=piece, source=p.name, page=page_no, chunk_id=global_id)
                )
                global_id += 1
    return all_chunks

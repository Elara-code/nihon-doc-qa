"""Streamlit 演示界面（Day 16-17）。

设计取舍：
- 只展示 RAG 该展示的：文档上传 / 提问 / 回答 / 出处 / 检索模式切换。
- 不做前端炫技，目标是面试演示时能跑完一遍流程。
- pipeline 用 @st.cache_resource 缓存，避免每次重运行都重载 bge-m3 / reranker
  模型（首次启动会慢，之后秒回）。
- 上传文件落到 data/uploads/ 临时目录后入库，不污染 samples/。

运行：
    streamlit run app.py
"""
from __future__ import annotations

import tempfile
import time
from pathlib import Path

import streamlit as st

from src.config import settings
from src.pipeline import RagPipeline


# ---------- 资源缓存 ----------
@st.cache_resource(show_spinner="正在加载模型（bge-m3 / reranker）…")
def get_pipeline() -> RagPipeline:
    """整个 session 共享一个 pipeline。"""
    return RagPipeline()


# ---------- 页面 ----------
st.set_page_config(
    page_title="対日技術文書 RAG 問答",
    page_icon="📄",
    layout="wide",
)

st.title("📄 対日技術文書 RAG 問答システム")
st.caption("中日双语 · 来源可追溯 · 支持纯向量 / 混合检索 / 重排序模式切换")

pipeline = get_pipeline()

# ---------- 侧栏：上传 + 检索模式 ----------
with st.sidebar:
    st.header("⚙️ 设置")

    mode = st.radio(
        "检索模式",
        options=["rerank", "hybrid", "vector"],
        index=0,
        help=(
            "vector = 仅向量检索（基线）\n"
            "hybrid = 向量 + BM25 RRF 融合\n"
            "rerank = hybrid 候选再用交叉编码器精排（默认，准确率最高）"
        ),
    )
    pipeline.retriever.mode = mode

    top_k = st.slider("Top-K（送给 LLM 的段落数）", 1, 15, settings.top_k)

    st.divider()
    st.subheader("📥 上传文档")
    uploaded = st.file_uploader(
        "PDF / TXT / MD（可多选）",
        type=["pdf", "txt", "md"],
        accept_multiple_files=True,
    )
    reset_db = st.checkbox("入库前清空已有索引", value=True)

    if st.button("入库", type="primary", disabled=not uploaded):
        with st.spinner("正在解析、切块、向量化…"):
            tmp_dir = Path(tempfile.mkdtemp(prefix="nihon_doc_qa_"))
            paths = []
            for f in uploaded:
                p = tmp_dir / f.name
                p.write_bytes(f.read())
                paths.append(p)
            t0 = time.time()
            n_chunks = pipeline.ingest(paths, reset=reset_db)
            elapsed = time.time() - t0
        st.success(
            f"已入库 {len(paths)} 份文档，{n_chunks} 个 chunk，耗时 {elapsed:.1f}s。"
        )

    st.divider()
    st.metric("当前索引 chunk 数", pipeline.store.count())

# ---------- 主区：提问 ----------
st.subheader("❓ 提问")

if "history" not in st.session_state:
    st.session_state.history = []  # [(query, result), ...]

query = st.text_input(
    "用中文或日文提问（例：エコセメントの経済効果試算額はいくらですか？）",
    value="",
)

col_ask, col_clear = st.columns([1, 1])
ask_clicked = col_ask.button("提问", type="primary", disabled=not query.strip())
if col_clear.button("清空历史"):
    st.session_state.history = []

if ask_clicked:
    if pipeline.store.count() == 0:
        st.warning("当前索引为空。请先在左侧上传并入库文档。")
    else:
        with st.spinner(f"检索 + 生成中（mode={mode}, top_k={top_k}）…"):
            t0 = time.time()
            result = pipeline.answer(query, top_k=top_k)
            elapsed = time.time() - t0
        result["_elapsed"] = elapsed
        result["_mode"] = mode
        result["_top_k"] = top_k
        st.session_state.history.insert(0, (query, result))

# ---------- 回答展示 ----------
for q, r in st.session_state.history:
    with st.container(border=True):
        st.markdown(f"**Q**：{q}")
        st.markdown(f"**A**：{r['answer']}")
        if r["citations"]:
            st.caption(r["citations"])
        meta_cols = st.columns(3)
        meta_cols[0].caption(f"⏱ 用时 {r['_elapsed']:.1f}s")
        meta_cols[1].caption(f"🔍 模式 {r['_mode']}")
        meta_cols[2].caption(f"📚 top_k {r['_top_k']}")

        with st.expander(f"查看检索命中的 {len(r['hits'])} 个段落（点开核对原文）"):
            for i, hit in enumerate(r["hits"], 1):
                meta = hit["metadata"]
                tags = [f"{meta.get('source','?')} p.{meta.get('page','?')}"]
                if "rerank_score" in hit:
                    tags.append(f"rerank={hit['rerank_score']:.3f}")
                elif "rrf_score" in hit:
                    tags.append(f"rrf={hit['rrf_score']:.4f}")
                elif "distance" in hit:
                    tags.append(f"dist={hit['distance']:.4f}")
                st.markdown(f"**#{i}** · {' · '.join(tags)}")
                st.text(hit["text"][:500] + ("…" if len(hit["text"]) > 500 else ""))
                st.divider()

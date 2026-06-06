"""Streamlit 演示界面（Day 16-17，UI 精修版）。

设计原则：
- 简约配色（中性灰 + 单一深色强调），无多余 emoji。
- 内容宽度封顶，留白足，参考 ChatGPT / Linear 风格。
- 检索模式做成分段控件感觉的 radio（横向、压扁、无圆点）。
- 回答 / 命中段落用卡片视觉，引文与元数据用 chip 风格。

运行：
    streamlit run app.py
"""
from __future__ import annotations

import html
import tempfile
import time
from pathlib import Path

import streamlit as st

from src.config import settings
from src.pipeline import RagPipeline


# ---------- 资源缓存 ----------
@st.cache_resource(show_spinner="正在加载模型（bge-m3 / reranker）…")
def get_pipeline() -> RagPipeline:
    return RagPipeline()


# ---------- 页面设置 ----------
st.set_page_config(
    page_title="対日技術文書 RAG 問答",
    page_icon="📄",
    layout="centered",
    initial_sidebar_state="expanded",
)


# ---------- 全局 CSS ----------
st.markdown(
    """
    <style>
      :root {
        --ink: #0f172a;
        --ink-soft: #475569;
        --line: #e5e7eb;
        --line-soft: #f1f5f9;
        --bg-soft: #f8fafc;
        --accent: #1f2937;
      }

      /* 隐藏 Streamlit 顶部菜单、footer */
      header[data-testid="stHeader"] { background: transparent; }
      #MainMenu, footer { visibility: hidden; }

      /* 主容器更窄、上边距更克制 */
      .main .block-container {
        max-width: 820px;
        padding-top: 2.5rem;
        padding-bottom: 4rem;
      }

      /* 标题排版 */
      h1, h2, h3, h4 {
        font-weight: 600;
        letter-spacing: -0.01em;
        color: var(--ink);
      }
      h1 { font-size: 1.7rem !important; margin-bottom: 0.25rem !important; }
      h2 { font-size: 1.15rem !important; margin-top: 1.5rem !important; }
      .app-subtitle {
        color: var(--ink-soft);
        font-size: 0.9rem;
        margin-bottom: 2rem;
      }

      /* 输入框 */
      .stTextInput > div > div > input {
        border-radius: 10px;
        border: 1px solid var(--line);
        padding: 0.7rem 0.9rem;
      }
      .stTextInput > div > div > input:focus {
        border-color: var(--accent);
        box-shadow: 0 0 0 3px rgba(31,41,55,0.08);
      }

      /* 按钮 */
      .stButton > button {
        border-radius: 8px;
        border: 1px solid var(--line);
        padding: 0.45rem 1rem;
        font-weight: 500;
        transition: all 0.15s ease;
      }
      .stButton > button:hover {
        border-color: var(--ink-soft);
        background: var(--bg-soft);
      }
      .stButton > button[kind="primary"] {
        background: var(--accent);
        color: white;
        border-color: var(--accent);
      }
      .stButton > button[kind="primary"]:hover {
        background: #111827;
        border-color: #111827;
      }
      .stButton > button:disabled {
        opacity: 0.45;
      }

      /* 侧栏 */
      [data-testid="stSidebar"] {
        background: var(--bg-soft);
        border-right: 1px solid var(--line);
      }
      [data-testid="stSidebar"] .block-container {
        padding-top: 2rem;
      }
      .sidebar-section {
        text-transform: uppercase;
        font-size: 0.72rem;
        letter-spacing: 0.08em;
        color: var(--ink-soft);
        font-weight: 600;
        margin: 0 0 0.5rem 0;
      }

      /* 检索模式 radio：压扁横排 */
      [data-testid="stSidebar"] [role="radiogroup"] {
        gap: 0.25rem;
      }
      [data-testid="stSidebar"] [role="radiogroup"] label {
        padding: 0.4rem 0.7rem;
        border: 1px solid var(--line);
        border-radius: 6px;
        background: white;
        cursor: pointer;
        flex: 1;
      }

      /* 回答卡片 */
      .qa-card {
        border: 1px solid var(--line);
        border-radius: 12px;
        padding: 1.25rem 1.5rem;
        margin-bottom: 1rem;
        background: white;
      }
      .qa-card .q {
        color: var(--ink-soft);
        font-size: 0.85rem;
        margin-bottom: 0.5rem;
      }
      .qa-card .a {
        color: var(--ink);
        font-size: 1rem;
        line-height: 1.65;
        white-space: pre-wrap;
      }
      .qa-card .cite {
        margin-top: 0.9rem;
        padding-top: 0.75rem;
        border-top: 1px solid var(--line-soft);
        color: var(--ink-soft);
        font-size: 0.82rem;
      }
      .qa-card .meta {
        margin-top: 0.5rem;
        display: flex;
        gap: 0.5rem;
        flex-wrap: wrap;
      }
      .chip {
        display: inline-flex;
        align-items: center;
        background: var(--line-soft);
        color: var(--ink-soft);
        border-radius: 999px;
        padding: 0.15rem 0.6rem;
        font-size: 0.74rem;
        font-variant-numeric: tabular-nums;
      }

      /* 命中段落展开块 */
      .hit-item {
        border-left: 2px solid var(--line);
        padding: 0.5rem 0 0.5rem 0.85rem;
        margin: 0.5rem 0 1rem 0;
      }
      .hit-head {
        font-size: 0.78rem;
        color: var(--ink-soft);
        margin-bottom: 0.35rem;
      }
      .hit-body {
        font-size: 0.86rem;
        line-height: 1.55;
        color: var(--ink);
        white-space: pre-wrap;
      }

      /* 空态 */
      .empty {
        color: var(--ink-soft);
        font-size: 0.9rem;
        padding: 1.5rem 0;
        text-align: center;
        border: 1px dashed var(--line);
        border-radius: 10px;
      }

      /* st.metric 微调 */
      [data-testid="stMetricValue"] {
        font-size: 1.1rem;
        font-weight: 600;
      }
      [data-testid="stMetricLabel"] {
        font-size: 0.74rem;
        color: var(--ink-soft);
      }
    </style>
    """,
    unsafe_allow_html=True,
)


pipeline = get_pipeline()


# ---------- 侧栏 ----------
with st.sidebar:
    st.markdown('<div class="sidebar-section">检索模式</div>', unsafe_allow_html=True)
    mode = st.radio(
        "检索模式",
        options=["rerank", "hybrid", "vector"],
        index=0,
        label_visibility="collapsed",
        help=(
            "vector — 仅向量检索（基线）\n"
            "hybrid — 向量 + BM25 RRF 融合\n"
            "rerank — hybrid 候选再用交叉编码器精排（默认，准确率最高）"
        ),
    )
    pipeline.retriever.mode = mode

    top_k = st.slider("Top-K", 1, 15, settings.top_k, help="送给 LLM 的段落数")

    st.markdown("---")
    st.markdown('<div class="sidebar-section">文档</div>', unsafe_allow_html=True)
    uploaded = st.file_uploader(
        "上传 PDF / TXT / MD",
        type=["pdf", "txt", "md"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )
    reset_db = st.checkbox("入库前清空已有索引", value=True)
    ingest_clicked = st.button(
        "入库", type="primary", disabled=not uploaded, use_container_width=True
    )

    if ingest_clicked:
        with st.spinner("解析、切块、向量化…"):
            tmp_dir = Path(tempfile.mkdtemp(prefix="nihon_doc_qa_"))
            paths = []
            for f in uploaded:
                p = tmp_dir / f.name
                p.write_bytes(f.read())
                paths.append(p)
            t0 = time.time()
            n_chunks = pipeline.ingest(paths, reset=reset_db)
            elapsed = time.time() - t0
        st.success(f"已入库 {len(paths)} 份 / {n_chunks} chunks · {elapsed:.1f}s")

    st.markdown("---")
    st.metric("索引中 chunk", pipeline.store.count())


# ---------- 主区 ----------
st.markdown("# 対日技術文書 RAG 問答")
st.markdown(
    '<div class="app-subtitle">中日双语 · 来源可追溯 · 三种检索模式可切换做 A/B</div>',
    unsafe_allow_html=True,
)

if "history" not in st.session_state:
    st.session_state.history = []

query = st.text_input(
    "提问",
    placeholder="用中文或日文提问，例如：エコセメントの経済効果試算額はいくらですか？",
    label_visibility="collapsed",
)

c1, c2, _ = st.columns([1, 1, 4])
ask_clicked = c1.button("提问", type="primary", disabled=not query.strip())
if c2.button("清空历史", disabled=not st.session_state.history):
    st.session_state.history = []

if ask_clicked:
    if pipeline.store.count() == 0:
        st.warning("当前索引为空，请先在左侧上传并入库文档。")
    else:
        with st.spinner(f"检索 + 生成中（{mode} · top_k={top_k}）…"):
            t0 = time.time()
            result = pipeline.answer(query, top_k=top_k)
            elapsed = time.time() - t0
        result["_elapsed"] = elapsed
        result["_mode"] = mode
        result["_top_k"] = top_k
        st.session_state.history.insert(0, (query, result))


# ---------- 历史回答 ----------
if not st.session_state.history:
    st.markdown(
        '<div class="empty">在上方输入问题开始 · 回答将带文档出处</div>',
        unsafe_allow_html=True,
    )

for q, r in st.session_state.history:
    cite_html = (
        f'<div class="cite">{html.escape(r["citations"])}</div>' if r["citations"] else ""
    )
    st.markdown(
        f"""
        <div class="qa-card">
          <div class="q">Q · {html.escape(q)}</div>
          <div class="a">{html.escape(r["answer"])}</div>
          {cite_html}
          <div class="meta">
            <span class="chip">{r["_mode"]}</span>
            <span class="chip">top_k {r["_top_k"]}</span>
            <span class="chip">{r["_elapsed"]:.1f}s</span>
            <span class="chip">{len(r["hits"])} 段命中</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander(f"查看检索命中的 {len(r['hits'])} 个段落"):
        for i, hit in enumerate(r["hits"], 1):
            meta = hit["metadata"]
            tags = [f"{meta.get('source','?')} · p.{meta.get('page','?')}"]
            if "rerank_score" in hit:
                tags.append(f"rerank={hit['rerank_score']:.3f}")
            elif "rrf_score" in hit:
                tags.append(f"rrf={hit['rrf_score']:.4f}")
            elif "distance" in hit:
                tags.append(f"dist={hit['distance']:.4f}")
            body = hit["text"][:500] + ("…" if len(hit["text"]) > 500 else "")
            st.markdown(
                f"""
                <div class="hit-item">
                  <div class="hit-head">#{i} · {' · '.join(tags)}</div>
                  <div class="hit-body">{html.escape(body)}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

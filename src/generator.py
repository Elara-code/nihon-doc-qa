"""Prompt 组装与 LLM 调用。

Week 1 阶段保持最朴素的做法：
- 把检索到的 chunk 按"[i] 来源 p.N\\n正文"拼成上下文。
- 系统提示要求模型"只用提供的上下文回答；不知道就说不知道"。
- 来源标注在 Week 2 (Day 7) 会做得更精致，本周仅保证可追溯。
"""
from __future__ import annotations

from openai import OpenAI

from src.config import settings
from src.text_utils import detect_language


SYSTEM_PROMPT = (
    "你是一个对日技术文档问答助手。"
    "请仅基于下面提供的『参考资料』回答问题；"
    "若参考资料中没有相关信息，请明确说『资料中未找到相关内容』，不要编造。"
    "回答尽量简洁，必要时引用参考资料中的原文。"
)

# 按提问语言自动适配回答语言（Day 8）
_LANG_INSTRUCTION = {
    "ja": "ユーザーは日本語で質問しています。必ず日本語で回答してください。",
    "zh": "用户用中文提问，请用中文回答。",
    "other": "请用与用户提问相同的语言回答；无法判断时默认使用中文。",
}


def language_instruction(query: str) -> str:
    return _LANG_INSTRUCTION[detect_language(query)]


def format_context(hits: list[dict]) -> str:
    lines: list[str] = []
    for i, hit in enumerate(hits, 1):
        meta = hit.get("metadata", {})
        src = meta.get("source", "?")
        page = meta.get("page", "?")
        lines.append(f"[{i}] {src} p.{page}\n{hit['text']}")
    return "\n\n".join(lines)


def build_user_prompt(query: str, hits: list[dict]) -> str:
    context = format_context(hits) if hits else "（无）"
    return (
        f"参考资料：\n{context}\n\n"
        f"用户问题：{query}\n\n"
        "请基于以上参考资料作答。"
    )


def format_citations(hits: list[dict]) -> str:
    """把命中 chunk 的来源去重后排成可溯源脚注。

    同一文件同一页只出现一次，保持检索命中的先后顺序。
    """
    seen: set[tuple[str, object]] = set()
    items: list[str] = []
    for hit in hits:
        meta = hit.get("metadata", {})
        src = meta.get("source", "?")
        page = meta.get("page", "?")
        key = (src, page)
        if key in seen:
            continue
        seen.add(key)
        items.append(f"{src} 第{page}页")
    if not items:
        return ""
    return "依据：" + "；".join(items)


class Generator:
    def __init__(self) -> None:
        if not settings.llm_api_key:
            raise RuntimeError("未配置 LLM_API_KEY，无法调用大模型。")
        self.client = OpenAI(
            api_key=settings.llm_api_key,
            base_url=settings.llm_base_url,
        )
        self.model = settings.llm_model

    def generate(self, query: str, hits: list[dict]) -> str:
        system = f"{SYSTEM_PROMPT}\n{language_instruction(query)}"
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": build_user_prompt(query, hits)},
            ],
            temperature=0.2,
        )
        return resp.choices[0].message.content or ""

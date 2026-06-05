"""Day 1 验收脚本：确认 LLM API 跑通。

用法：
    python scripts/test_llm.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from openai import OpenAI
from src.config import settings


def main() -> None:
    if not settings.llm_api_key:
        raise SystemExit(
            "未检测到 LLM_API_KEY，请先复制 .env.example 为 .env 并填入 API Key。"
        )

    client = OpenAI(api_key=settings.llm_api_key, base_url=settings.llm_base_url)
    resp = client.chat.completions.create(
        model=settings.llm_model,
        messages=[
            {"role": "system", "content": "你是一个简洁的助手。"},
            {"role": "user", "content": "你好，用一句话自我介绍。"},
        ],
        temperature=0.3,
    )
    print("模型:", settings.llm_model)
    print("回复:", resp.choices[0].message.content)


if __name__ == "__main__":
    main()

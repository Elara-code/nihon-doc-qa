"""Day 9-10 批量测试：跑完整问题集，打印回答、出处、关键词命中。

这不是自动评分（那是第 4 周的事），而是帮你快速肉眼复盘——
哪些问题答得好、哪些差，把差的记进 docs/known-issues.md。

用法：
    python scripts/test_batch.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.pipeline import RagPipeline
from src.text_utils import detect_language

ROOT = Path(__file__).resolve().parents[1]


def keyword_hit(text: str, keywords: list[str]) -> bool:
    """关键词只要命中任意一个即视为相关（粗略的人工判断辅助）。"""
    return any(k in text for k in keywords)


def main() -> None:
    spec = json.loads((ROOT / "eval" / "test_questions.json").read_text(encoding="utf-8"))
    doc = ROOT / spec["doc"]

    pipeline = RagPipeline()
    n = pipeline.ingest([doc], reset=True)
    print(f"[ingest] {doc.name} -> {n} chunks\n")

    total = len(spec["questions"])
    hit_count = 0
    lang_ok = 0
    for q in spec["questions"]:
        result = pipeline.answer(q["question"])
        answer = result["answer"]
        hit = keyword_hit(answer, q["expect_keywords"])
        hit_count += hit
        # 回答语言是否与提问语言一致
        ans_lang = detect_language(answer)
        lang_match = ans_lang == q["lang"] or ans_lang == "other"
        lang_ok += lang_match

        print(f"========== {q['id']} [{q['lang']}] {q['note']} ==========")
        print(f"Q: {q['question']}")
        print(f"A: {answer}")
        print(f"   关键词命中: {'✅' if hit else '❌'}  期望含: {q['expect_keywords']}")
        print(f"   回答语言: {ans_lang}（提问 {q['lang']}）{'✅' if lang_match else '⚠️'}")
        print(f"   {result['citations']}")
        print()

    print("=" * 50)
    print(f"关键词命中率：{hit_count}/{total} = {hit_count / total:.0%}")
    print(f"语言一致率：{lang_ok}/{total} = {lang_ok / total:.0%}")
    print("（关键词命中只是粗筛，最终好坏请肉眼确认并记入 docs/known-issues.md）")


if __name__ == "__main__":
    main()

"""Day 13-15 验收脚本：三种检索模式横向对比，产出面试用的对比素材。

对每个测试问题，分别用 vector / hybrid / rerank 三种模式跑完整问答，
统计关键词命中，并把结果保存成 docs/retrieval-comparison.md。

用法：
    python scripts/compare_retrieval.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.pipeline import RagPipeline

ROOT = Path(__file__).resolve().parents[1]
MODES = ["vector", "hybrid", "rerank"]


def keyword_hit(text: str, keywords: list[str]) -> bool:
    return any(k in text for k in keywords)


def main() -> None:
    spec = json.loads((ROOT / "eval" / "test_questions.json").read_text(encoding="utf-8"))
    doc = ROOT / spec["doc"]
    questions = spec["questions"]

    # 三种模式共用同一份向量库；用不同 retrieval_mode 的 pipeline
    pipelines = {m: RagPipeline(retrieval_mode=m) for m in MODES}
    n = pipelines["vector"].ingest([doc], reset=True)
    for m in MODES[1:]:
        pipelines[m].retriever.refresh()
    print(f"[ingest] {doc.name} -> {n} chunks\n")

    hit_counts = {m: 0 for m in MODES}
    lines = ["# 检索模式对比（vector / hybrid / rerank）\n"]
    lines.append(f"测试集：`{spec['doc']}`，共 {len(questions)} 题。\n")

    for q in questions:
        lines.append(f"\n## {q['id']} [{q['lang']}] {q['note']}")
        lines.append(f"**Q**: {q['question']}  ")
        lines.append(f"**期望关键词**: {q['expect_keywords']}\n")
        lines.append("| 模式 | 命中 | 回答（截断） |")
        lines.append("|------|------|------|")
        print(f"========== {q['id']} {q['question']} ==========")
        for m in MODES:
            result = pipelines[m].answer(q["question"])
            ans = result["answer"]
            hit = keyword_hit(ans, q["expect_keywords"])
            hit_counts[m] += hit
            mark = "✅" if hit else "❌"
            short = ans.replace("\n", " ")[:60]
            lines.append(f"| {m} | {mark} | {short}… |")
            print(f"  {m:7s} {mark} {short}")
        print()

    total = len(questions)
    lines.append("\n## 汇总\n")
    lines.append("| 模式 | 关键词命中率 |")
    lines.append("|------|------|")
    for m in MODES:
        lines.append(f"| {m} | {hit_counts[m]}/{total} = {hit_counts[m] / total:.0%} |")

    out = ROOT / "docs" / "retrieval-comparison.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("=" * 50)
    for m in MODES:
        print(f"{m:7s} 命中率：{hit_counts[m]}/{total} = {hit_counts[m] / total:.0%}")
    print(f"\n对比结果已写入 {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

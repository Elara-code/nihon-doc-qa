"""正式评估脚本（Day 18-19）。

两种判分方式，写进同一份报告：
1. **关键词命中**（keyword）：粗筛、零成本、可在没有 LLM 裁判时降级使用。
2. **LLM-as-judge**（llm）：用同一个 LLM 当裁判，按"答案是否回应了问题且与参考关键词
   语义一致"打 0/1。比关键词命中更鲁棒——同义词、释义、跨语言回答都能正确判分。
   裁判 prompt 强约束 JSON 输出，再单题反序列化，单题失败不影响整体。

用法：
    python eval/evaluate.py                # 当前默认模式（rerank）一次评估
    python eval/evaluate.py --all-modes    # vector/hybrid/rerank 三模式横向评估
    python eval/evaluate.py --judge llm    # 加 LLM 裁判（需 LLM_API_KEY）
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.config import settings
from src.pipeline import RagPipeline

JUDGE_SYSTEM = (
    "你是一个严格的问答评判员。"
    "给定问题、参考关键词、被评回答。"
    "只要回答**实质上**回答了问题，且与参考关键词的语义一致（同义、释义、跨语言均可），"
    "判 correct=true；如果回答错误、缺失关键事实、或编造，判 correct=false。"
    "若关键词期望是『未找到/拒答』，则只要回答明确拒答即判 true。"
    "只输出 JSON：{\"correct\": true/false, \"reason\": \"一句话理由\"}"
)


@dataclass
class QResult:
    qid: str
    lang: str
    question: str
    expect_keywords: list[str]
    answer: str
    citations: str
    keyword_hit: bool
    llm_correct: bool | None = None
    llm_reason: str = ""


@dataclass
class ModeReport:
    mode: str
    results: list[QResult] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.results)

    def acc(self, judge: Literal["keyword", "llm"]) -> float:
        if not self.results:
            return 0.0
        if judge == "keyword":
            return sum(r.keyword_hit for r in self.results) / self.total
        scored = [r for r in self.results if r.llm_correct is not None]
        if not scored:
            return 0.0
        return sum(r.llm_correct for r in scored) / len(scored)


def keyword_hit(answer: str, keywords: list[str]) -> bool:
    return any(k in answer for k in keywords)


def llm_judge(question: str, expect: list[str], answer: str) -> tuple[bool | None, str]:
    """让同款 LLM 当裁判。单题失败返回 (None, error)，不影响整体评估。"""
    try:
        from openai import OpenAI

        client = OpenAI(api_key=settings.llm_api_key, base_url=settings.llm_base_url)
        user = (
            f"问题：{question}\n"
            f"参考关键词：{expect}\n"
            f"被评回答：{answer}"
        )
        resp = client.chat.completions.create(
            model=settings.llm_model,
            messages=[
                {"role": "system", "content": JUDGE_SYSTEM},
                {"role": "user", "content": user},
            ],
            temperature=0.0,
            response_format={"type": "json_object"},
        )
        raw = resp.choices[0].message.content or "{}"
        # 兜底：万一模型把 JSON 包在代码块里
        m = re.search(r"\{.*\}", raw, re.DOTALL)
        data = json.loads(m.group() if m else raw)
        return bool(data.get("correct", False)), str(data.get("reason", ""))[:200]
    except Exception as e:
        return None, f"judge_error: {e}"


def evaluate_one_mode(
    spec: dict,
    pipeline: RagPipeline,
    mode: str,
    use_llm_judge: bool,
) -> ModeReport:
    pipeline.retriever.mode = mode
    report = ModeReport(mode=mode)
    for q in spec["questions"]:
        result = pipeline.answer(q["question"])
        ans = result["answer"]
        kw = keyword_hit(ans, q["expect_keywords"])
        r = QResult(
            qid=q["id"],
            lang=q["lang"],
            question=q["question"],
            expect_keywords=q["expect_keywords"],
            answer=ans,
            citations=result["citations"],
            keyword_hit=kw,
        )
        if use_llm_judge:
            r.llm_correct, r.llm_reason = llm_judge(q["question"], q["expect_keywords"], ans)
        report.results.append(r)
        # 单行进度
        marks = "✅" if kw else "❌"
        if use_llm_judge:
            marks += " " + ("✅" if r.llm_correct else ("?" if r.llm_correct is None else "❌"))
        print(f"  [{mode:7s}] {q['id']:>3s} {marks}  {ans[:50].replace(chr(10),' ')}")
    return report


def write_report(
    reports: list[ModeReport], out: Path, judge: str
) -> None:
    lines: list[str] = []
    lines.append("# 评估报告\n")
    lines.append(f"判分方式：**{judge}**（keyword=关键词命中；llm=LLM-as-judge）\n")
    # 汇总
    lines.append("## 准确率汇总\n")
    lines.append("| 模式 | 关键词命中率 | " + ("LLM 裁判通过率 |" if judge == "llm" else ""))
    lines.append("|------|------|" + ("------|" if judge == "llm" else ""))
    for rep in reports:
        kw = rep.acc("keyword")
        cols = [rep.mode, f"{kw:.0%} ({sum(r.keyword_hit for r in rep.results)}/{rep.total})"]
        if judge == "llm":
            scored = [r for r in rep.results if r.llm_correct is not None]
            llm = rep.acc("llm")
            cols.append(f"{llm:.0%} ({sum(r.llm_correct for r in scored)}/{len(scored)})")
        lines.append("| " + " | ".join(cols) + " |")
    # 逐题
    for rep in reports:
        lines.append(f"\n## 模式：{rep.mode}\n")
        for r in rep.results:
            lines.append(f"\n### {r.qid} [{r.lang}]")
            lines.append(f"**Q**：{r.question}  ")
            lines.append(f"**期望关键词**：`{r.expect_keywords}`  ")
            lines.append(f"**A**：{r.answer}")
            if r.citations:
                lines.append(f"\n> {r.citations}")
            tags = [f"keyword={'✅' if r.keyword_hit else '❌'}"]
            if r.llm_correct is not None:
                tags.append(f"llm={'✅' if r.llm_correct else '❌'} （{r.llm_reason}）")
            lines.append("\n" + " · ".join(tags))
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--all-modes", action="store_true", help="对 vector/hybrid/rerank 三模式做横向评估")
    parser.add_argument("--judge", choices=["keyword", "llm"], default="keyword")
    parser.add_argument("--out", default="docs/evaluation-report.md")
    args = parser.parse_args()

    spec = json.loads((ROOT / "eval" / "test_questions.json").read_text(encoding="utf-8"))
    doc = ROOT / spec["doc"]

    pipeline = RagPipeline()
    n = pipeline.ingest([doc], reset=True)
    print(f"[ingest] {doc.name} -> {n} chunks\n")

    modes = ["vector", "hybrid", "rerank"] if args.all_modes else [settings.retrieval_mode]
    reports: list[ModeReport] = []
    use_llm = args.judge == "llm"
    for m in modes:
        print(f"========== mode = {m} ==========")
        reports.append(evaluate_one_mode(spec, pipeline, m, use_llm_judge=use_llm))
        print()

    out = ROOT / args.out
    write_report(reports, out, judge=args.judge)
    print("=" * 50)
    for rep in reports:
        kw = rep.acc("keyword")
        msg = f"{rep.mode:7s}  关键词命中率 {kw:.0%}"
        if use_llm:
            msg += f"  |  LLM 裁判通过率 {rep.acc('llm'):.0%}"
        print(msg)
    print(f"\n报告已写入 {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

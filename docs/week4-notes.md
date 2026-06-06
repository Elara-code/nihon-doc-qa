# Week 4 复盘：界面 + 评估

> 第 4 周目标：让别人能点开就用、并且能说清楚"系统好不好"。

## 本周交付

- ✅ Day 16-17：Streamlit 演示界面（`app.py`）
- ✅ Day 18-19：正式评估脚本（`eval/evaluate.py`，含 LLM-as-judge）
- ✅ Day 20：演示录屏脚本（`docs/demo-script.md`，待你本地完成录屏）

---

## Day 16-17：Streamlit 界面

### 设计思路（这套话面试时可以直接讲）
- 不做前端炫技。**RAG 应用的 demo 界面价值在"能立刻演示"，不在 UI**。
- 关键要素只有四个：**文档上传** / **模式切换** / **提问** / **回答+出处**。
- 加了一个"检索命中段落"的展开块——这是让面试官**一眼相信"真的基于检索"**
  的关键，而不是"LLM 凭印象答的"。

### 工程要点
- `@st.cache_resource` 缓存 pipeline，避免每次 rerun 重载 bge-m3 / reranker。
- 模式切换是**热切换**：直接改 `pipeline.retriever.mode`，无需重建索引。
  → 这让 demo 时同一题切模式对比成本极低（参见 `demo-script.md`）。
- 上传文件落到 `tempfile.mkdtemp` 临时目录再入库，不污染 `samples/`。

---

## Day 18-19：评估

### 为什么不只用关键词命中
关键词命中是 Week 3 用的"粗筛"——零成本，但有两个坑：
- **同义词/释义**：答案对但用词不同会判错。
- **跨语言回答**：中文问、日文答（或反过来）容易被关键词逻辑误伤。

所以 Day 18 加了 **LLM-as-judge**：让同款 deepseek-chat 当裁判，按
"答案是否实质回应问题、与参考关键词语义一致"打 0/1，
`response_format=json_object` 强约束输出，单题失败不影响整体。

### 工程要点
- 两种判分**并存**：报告里同时显示关键词命中率和 LLM 通过率，互为印证。
- LLM 裁判可关：`--judge keyword` 退化为零成本评估，CI 友好。
- 三模式横向：`--all-modes` 一次跑完 vector / hybrid / rerank。

### 用法

```bash
# 最快：当前模式 + 关键词命中
python eval/evaluate.py

# 横向对比 + LLM 裁判（推荐放进作品集的版本）
python eval/evaluate.py --all-modes --judge llm
```

### 准确率（待回填）

跑完后把 `docs/evaluation-report.md` 顶部的汇总表抄过来：

| 模式 | 关键词命中率 | LLM 裁判通过率 |
|------|------|------|
| vector | _填_ | _填_ |
| hybrid | _填_ | _填_ |
| rerank | _填_ | _填_ |

> Week 3 实测：keyword 8/7/10 = 67/58/83%。LLM 裁判的数字预期会**略高**
> （能识别正确但用词不同的回答）。这两个数字一起呈现，比单一指标更可信。

---

## Day 20：演示素材

`docs/demo-script.md` 是录屏指南——分钟级时间轴、关键叙事、ffmpeg 转 GIF 命令、
README 嵌入代码片段。**核心叙事**：同一题切换 vector / rerank 模式，结果不同
——这是让面试官立刻看懂"做了优化对比"的最快方式。

---

## 面试 2 句话版本

1. **界面**：Streamlit 三栏式 demo，**支持现场切换检索模式做 A/B**——这不是
   炫技，而是让面试官一眼看见 Week 3 的优化是真的有效，不是 PPT。
2. **评估**：关键词命中（粗筛、零成本）+ LLM-as-judge（鲁棒、可识别同义/跨语言）
   双轨判分；三种检索模式横向数字写进 `docs/evaluation-report.md`。

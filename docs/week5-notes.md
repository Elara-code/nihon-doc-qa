# Week 5 复盘：部署 + 文档

> 第 5 周目标：项目能被别人访问，GitHub 上有像样的门面。

## 本周交付

- ✅ Day 21-22：Docker 化（`Dockerfile` + `.dockerignore`）
- ✅ Day 23：HF Spaces 部署指南（`docs/deployment.md`）
- ✅ Day 24-25：README 全面打磨

---

## Day 21-22：Docker 化

### 取舍：轻量镜像（运行时下载模型）

bge-m3 + bge-reranker-v2-m3 加起来约 2.5GB。两种选择：

| | 轻量镜像（本项目选） | 胖镜像 |
|---|---|---|
| 镜像体积 | < 2GB | ~3.5GB |
| 首次启动 | 慢（下载 1-2 分钟） | 秒级 |
| 适合 HF Spaces | ✅ | ❌（超上传限制） |
| 离线可用 | ❌ | ✅ |

选轻量是为对齐 HF Spaces 主部署目标。挂载 `-v $(pwd)/.cache:/app/.cache/huggingface`
解决"本地反复启动重新下载"的体验问题。

### 关键细节
- `python:3.11-slim` 基底，只装 `build-essential / ca-certificates / curl`
- 分层：先 `COPY requirements.txt && pip install`，再 `COPY src/ app.py`，
  改源码时不重装依赖
- `HF_HOME` / `SENTENCE_TRANSFORMERS_HOME` 都指 `/app/.cache/huggingface`，
  方便挂载持久化
- Streamlit `--server.address=0.0.0.0 --headless=true`，否则容器外访问不到

---

## Day 23：HF Spaces 部署

### 为什么选 HF Spaces

- 完全免费（CPU basic 16GB RAM 够跑 bge-m3 + reranker）
- 原生 Docker SDK 支持（README YAML 声明 `sdk: docker`）
- HF 是 AI 工程社区，作品集放这里有圈内可见度

### 关键操作（详见 `docs/deployment.md`）

1. 在 HF 创建 Space，**SDK 选 Docker**（不是 Streamlit！）
2. 在 README 顶部加 YAML frontmatter：

   ```yaml
   ---
   sdk: docker
   app_port: 8501
   ---
   ```

3. Space Settings → Repository secrets 加 `LLM_API_KEY`
4. `git remote add hf https://huggingface.co/spaces/<你>/nihon-doc-qa`
5. `git push hf develop:main`

部署后 HF 自动构建镜像 + 跑容器，首次启动需 1-2 分钟下载模型——
这一点在 deployment.md 里写明了「不是卡死」的提示。

---

## Day 24-25：README 打磨

把全部占位符（`约 X%`、`<N>`、`<这里放...>`）替换成真实数据，关键设计决策段
写进 4 个真实故事：

1. **混合检索**：诚实说 hybrid 最终命中率没提升，价值在召回层
2. **Rerank**：92% 是赢家，Q10/Q11 是干净的归因例子
3. **伪换行 bug**：1874 处定位 + 最小修复（工程定位能力素材）
4. **主题混杂 chunk**：不修，给出生产环境分档方案（top_k → Small-to-Big → Contextual Retrieval）

第 4 点是面试的杀手锏——展示"我懂哪些值得做、哪些是 ROI 低的炫技"。

---

## 面试 1 句话版本

> 项目部署在 Hugging Face Spaces，URL 可点试；README 顶部有 vector vs rerank 的
> 截图对比和 67% → 92% 的硬数字，关键设计决策段有 4 个『问题→方案→效果』故事，
> 其中包括一个**沿途定位并修复的 PDF 段内伪换行 bug**（1874 处），
> 以及一个**故意没修但说清楚生产环境怎么修**的『主题混杂 chunk』问题。

---

## 5 周总结

| 周 | 主线 | 交付 |
|---|---|---|
| 1 | 朴素 RAG | 跑通"解析→向量化→检索→生成"全链路 |
| 2 | 对日特色 | 中日规整、来源标注、双语回答、双语测试集 |
| 3 | 检索优化 | 混合检索（RRF）+ Rerank，命中率 67→92% |
| 4 | 界面 + 评估 | Streamlit 简约 UI + LLM-as-judge 双轨评估 |
| 5 | 部署 + 文档 | Docker + HF Spaces + 作品集级 README |

差异化最强的是：**真实数据 + 双轨评估 + 诚实记录 hybrid 平、Q4/Q7 失败 + 工程定位 bug 修复 + 主动留下生产优化路径**。
和"跟教程拼装的 RAG demo"之间的差距，就在这些细节。

# 演示素材脚本（Day 20）

> 目标：4 张关键截图放进 README，让面试官 5 秒看懂"做了 RAG 优化对比"。
> 视频不是必须——HR 简历筛选阶段几乎不会点视频；真正的"动态 demo"
> 留给 Week 5 部署到 Hugging Face Spaces 的在线链接。

## 截图清单（4 张，按 README 出现顺序）

放进 `docs/screenshots/`，命名建议如下：

| # | 文件名 | 内容 | 价值 |
|---|--------|------|------|
| 1 | `01-overview.png` | 整体界面（空态，侧栏 + 主区都在画面） | 体现简约 UI 设计 |
| 2 | `02-ingest.png` | 入库完成的状态（绿色提示 "已入库 1 份 / 264 chunks · 49.4s"） | 证明文档处理链路 |
| 3 | `03-rerank-answer.png` | 用 rerank 模式问 `エコセメントの経済効果試算額はいくらですか？`，答案 5920億4百万円 + 多页出处 + chip 元数据 | 证明回答正确且可溯源 |
| 4 | `04-vector-vs-rerank.png` | 切到 vector 模式重问同一题，**vector 答"未找到"在上、rerank 答对在下同框出现**（历史栈天然形成 before/after） | **🔥 一张图讲完优化叙事** |

> 第 4 张是杀手锏——历史回答栈把 vector ❌ 和 rerank ✅ 在同一屏内同时呈现，
> 面试官 2 秒就懂。

## 怎么拍这 4 张（macOS）

`Cmd + Shift + 4` 进入区域截图；按空格切换到窗口截图。
建议把浏览器先 `Cmd + Ctrl + F` 全屏，避免书签栏、标签页泄露隐私信息。

### 拍摄顺序

1. **空界面** → 截 `01-overview.png`
2. 上传 `samples/houkokusho_sample.pdf` → 点入库 → 等绿色提示出来 → 截 `02-ingest.png`
3. 检索模式选 `rerank`，问 `エコセメントの経済効果試算額はいくらですか？` → 截 `03-rerank-answer.png`
4. **不要清空历史**，把检索模式切到 `vector`，**重问同一题** → 此时屏幕上 vector ❌（在上）和 rerank ✅（在下）同时出现 → 截 `04-vector-vs-rerank.png`

## 放进 README 的代码片段

```markdown
## 演示

![整体界面](docs/screenshots/01-overview.png)

### 优化效果对比（同一道日文问题，切换检索模式）

| rerank 模式（默认） | vector 模式（基线） |
|---|---|
| ![](docs/screenshots/03-rerank-answer.png) | ![](docs/screenshots/04-vector-vs-rerank.png) |
| ✅ `资料によると、エコセメントの経済効果試算額は **5920億4百万円** です（[1] p.61）。` | ❌ `資料中未找到相关内容。` |

> 同一份 264 chunk 的 PDF、同一道问题，纯向量检索找不到深埋第 61 页的数值；
> rerank 模式（向量 + BM25 + 交叉编码器）准确召回并回答。
> 测试集 12 题，关键词命中率 **67% → 92%（+25pp）**。详见 [评估报告](docs/evaluation-report.md)。
```

## 视频（可选，不是必须）

如果你想录一段用于**面试时自己 share screen**（README 不用嵌入）：

- 时长 1-2 分钟，节奏：上传 → 入库 → 问题 → rerank 答对 → 切 vector 答不出 → 切回 rerank。
- macOS QuickTime 录制；先 `Cmd + Ctrl + F` 全屏浏览器避免泄露。

### 压缩命令（如有需要）

```bash
# GIF（README 用，目标 ≤8MB）
ffmpeg -i demo.mov -vf "fps=8,scale=720:-1:flags=lanczos,palettegen" -y /tmp/palette.png
ffmpeg -i demo.mov -i /tmp/palette.png -lavfi "fps=8,scale=720:-1:flags=lanczos [x]; [x][1:v] paletteuse" -loop 0 docs/demo.gif

# MP4（小且清晰，无音轨）
ffmpeg -i demo.mov -vcodec libx264 -crf 28 -preset slow -vf "scale=1280:-2" -an docs/demo.mp4

# 顶部裁掉浏览器导航栏（150px 视情况调）
ffmpeg -i demo.mov -vf "crop=in_w:in_h-150:0:150" -c:a copy demo-clean.mov
```

## 验收

- [x] 4 张截图（`01`-`04`）放进 `docs/screenshots/`
- [ ] README 顶部能渲染出 demo 区块（GitHub 上预览正常）
- [ ] _（可选）_ 视频备一段用于面试 share screen

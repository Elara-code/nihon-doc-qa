# 演示录屏 / 截图脚本（Day 20）

> 目标：1-2 分钟的 demo 视频（或 GIF）+ 几张关键截图，放进 README。
> 时长不超 2 分钟，节奏紧凑。**先打开 .env、确认 API key 填好**。

## 录屏前的准备

1. 浏览器窗口拖到 1280×800 左右（GIF 体积友好，README 渲染清晰）。
2. 关掉 macOS 通知（钉钉/微信/系统提示），避免遮挡或意外弹窗。
3. 终端字号调大（讲解时观众看得清）。
4. 启动应用：

   ```bash
   streamlit run app.py
   ```

   首次会加载 bge-m3 / reranker（看到「正在加载模型」spinner 转完）。

## 录屏脚本（1 分 30 秒）

| 时间 | 屏幕动作 | 旁白要点（可不录音，只走画面） |
|------|---------|---------|
| 0:00-0:10 | 显示空界面 | "对日技术文档 RAG 问答系统，中日双语，可溯源" |
| 0:10-0:25 | 左侧上传 `samples/houkokusho_sample.pdf`，点入库，等约 20-40s | "支持 PDF/TXT，自动切块向量化入库" |
| 0:25-0:35 | 入库成功显示 chunk 数 | "264 chunk 入库完成" |
| 0:35-0:55 | 输入日文问题 `ITU-Tは何を指す略称ですか？` → 回答 → 展开命中段落 | "日文提问，日文回答，附文档出处" |
| 0:55-1:15 | 把检索模式切到 `vector`，重问同一题 → 回答"未找到" | "对比：纯向量检索找不到 ITU-T 全称" |
| 1:15-1:30 | 切回 `rerank` → 答对 | "rerank 模式正确回答——这就是优化的价值" |

> 关键叙事：**同一题，切换模式，结果不同**——这是面试看到 demo 时
> 立刻明白"哦你真做了优化对比"的最快方式。

## 推荐用工具

- macOS 自带 **QuickTime**：File → New Screen Recording。导出 .mov。
- 转 GIF：`ffmpeg -i demo.mov -vf "fps=10,scale=900:-1" -loop 0 docs/demo.gif`
  （fps 调低、宽度压到 900px，控制在 5MB 内便于 README）。
- 不想录音：MOV/MP4 上传到 YouTube（不公开链接也行），README 嵌入封面图。

## 截图清单（4 张够用）

放进 `docs/screenshots/`，然后在 README 里引用。

1. **整体界面**：刚打开、侧栏 + 主区都在画面里。
2. **入库完成**：左侧显示 "已入库 1 份文档，264 chunk"。
3. **回答 + 出处**：一道日文问题的完整回答，「依据：houkokusho_sample.pdf 第3页」清晰可见。
4. **检索命中段落展开**：那个 expander 展开后，能看到 #1 命中段落、rerank_score 等元数据——
   面试官一眼就懂"哦真的是基于检索答的，不是 LLM 凭空编"。

## 给 README 的展示代码片段

录屏完把文件放 `docs/demo.gif`、截图放 `docs/screenshots/01-*.png` 等，
README 顶部加：

```markdown
## 演示

![演示](docs/demo.gif)

| 上传 + 入库 | 中日问答 + 出处 | 检索命中段落 |
|---|---|---|
| ![](docs/screenshots/02-ingest.png) | ![](docs/screenshots/03-answer.png) | ![](docs/screenshots/04-hits.png) |
```

## 验收

- [ ] 1-2 分钟的 .gif 或 .mp4
- [ ] 4 张关键截图
- [ ] README 能渲染出 demo（GitHub 上预览正常）

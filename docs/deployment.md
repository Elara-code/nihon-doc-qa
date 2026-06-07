# 部署指南

## 本地用 Docker 跑（Day 21-22 验收）

```bash
# 1. 构建镜像（约 5-10 分钟，看网络）
docker build -t nihon-doc-qa .

# 2. 跑起来（把你本地 .env 里的 LLM_API_KEY 传给容器）
docker run --rm -p 8501:8501 \
  -e LLM_API_KEY=$LLM_API_KEY \
  -v $(pwd)/.cache:/app/.cache/huggingface \
  nihon-doc-qa
```

`-v $(pwd)/.cache:/app/.cache/huggingface` 把 HuggingFace 模型缓存挂出来——
首次启动会下载 ~2.5GB 模型，之后再启动就秒级。

浏览器打开 http://localhost:8501，看到界面 = Day 21-22 ✅。

---

## Hugging Face Spaces 部署（Day 23）

### 为什么选 HF Spaces？

- **完全免费**（CPU basic 层 16GB RAM，够跑 bge-m3 + reranker）
- **原生 Docker SDK 支持**——README 里的 YAML frontmatter 就声明了 `sdk: docker`
- **HF 是 AI 工程社区**，作品集放这里有"圈内可见"信号

### 一次性配置

1. **注册 / 登录** [huggingface.co](https://huggingface.co)
2. **创建 Space**：右上角 New → Space
   - Owner: 你的用户名
   - Space name: `nihon-doc-qa`（或你喜欢的）
   - License: MIT
   - SDK: 选 **Docker**（不是 Streamlit！我们要用自己的 Dockerfile）
   - Hardware: **CPU basic**（免费，16GB RAM 够用）
   - Visibility: Public
3. **绑定 git 远端**：

   ```bash
   # 在项目根目录
   git remote add hf https://huggingface.co/spaces/<你的用户名>/nihon-doc-qa
   ```

4. **配置 LLM_API_KEY**：在 Space 页面 → Settings → Repository secrets →
   Add secret，Name = `LLM_API_KEY`，Value = 你的 Deepseek key。
   容器启动时这个 secret 会作为环境变量注入，pipeline 自动读到。

### 每次部署

```bash
# 把 develop 或 main 推到 HF（HF 默认分支是 main）
git push hf develop:main
```

HF 看到推送后会自动：
1. 用你的 `Dockerfile` 构建镜像（约 5-10 分钟）
2. 跑容器，首次启动下载模型（约 1-2 分钟）
3. 在 `https://huggingface.co/spaces/<你>/nihon-doc-qa` 提供 web 入口

### 首次启动的"假死"提示

首次容器启动时 Streamlit 会显示「正在加载模型」spinner，**可能持续 1-2 分钟**——
不是卡死，是 sentence-transformers 在下载 bge-m3。耐心等。

之后 HF Spaces 会把模型缓存到 Space 的存储（Hub LFS）里，重启会快很多。

---

## 部署后要做的两件事

1. **把 Space URL 更新到 README**：把 `🚧 在线试用` 那一行替换成真链接。
2. **在 Space 里跑一次完整流程验证**：
   - 上传 `samples/houkokusho_sample.pdf`
   - 用 rerank 模式问 `エコセメントの経済効果試算額はいくらですか？`
   - 应该看到 5920億4百万円 的回答 + 出处
   - 切到 vector 模式重问 → 应该「未找到」
   - 这就是 demo 的核心叙事，留个截图也行

---

## 排错

| 现象 | 原因 | 修法 |
|---|---|---|
| Space 构建失败 | requirements.txt 装包超时 | 重试一次；persistent failure 检查 HF 网络 |
| 启动后立刻 502 | port 不匹配 | 确认 README YAML 里 `app_port: 8501` 和 Dockerfile EXPOSE 一致 |
| 提问报 `LLM_API_KEY 未配置` | 没设 secret | Space Settings → Repository secrets → 加 `LLM_API_KEY` |
| 模型下载 OOM | 16GB 不够（极少见） | 升级 Space 到 CPU upgrade（付费）；或在 .env 改用更小的 embedding 模型 |

# Week 1 复盘笔记

> 一路上踩到的坑和当时的解决思路。这是面试时讲"我做了什么"的真实素材。

## 本周交付

第 1 周目标：跑通最朴素的 RAG 链路。结果：

- ✅ Day 1：项目骨架 + Deepseek API 连通（`scripts/test_llm.py`）
- ✅ Day 2：PyMuPDF 解析 + 字符滑窗切块（`scripts/test_chunking.py`）
- ✅ Day 3：bge-m3 向量化 + Chroma 持久化 + top-k 检索（`scripts/test_retrieval.py`）
- ✅ Day 4：朴素 RAG 全链路打通，提问可得到带出处的回答（`scripts/test_rag.py`）
- ✅ Day 5：整理 + 推送

## 关键设计决策

### 为什么 embedding 在 VectorStore 外面算？
Chroma 自带 embedding function，但我把它解耦：
`Embedder` 负责把文本→向量，`VectorStore` 只接收向量。
好处：换 embedding 模型时不用动向量库，第 3 周做 rerank/混合检索时复用方便。

### 为什么按字符切块而不是按 token？
中日文本一个汉字/假名就是一个有意义的语义单元，按字符切对阅读和调试更直观。
缺点是不能直接对应 LLM 的 token budget，未来如果上下文长度成问题再换。

### Generator 为什么惰性初始化？
`RagPipeline()` 不该在没有 API key 的环境下就崩溃——
比如只想本地试切块/检索时。把 LLM client 推迟到真正调用 `answer()` 时才创建。

## 遇到的问题

> 实际跑的时候把踩到的坑写在这里，比如：
> - bge-m3 模型首次下载很慢，加了进度提示
> - Chroma 集合重名报错，加了 reset() 方法
> - 中日混排 PDF 提取出乱码，xx 模型不行，换 yy 解决

（按真实情况填）

## 已知问题（第 2 周输入）

- 来源标注只在 hit 元数据里，没在最终回答里显式呈现 → Day 7 处理
- 提示语没有指定"按提问语言回答"，模型可能用错语言 → Day 8 处理
- 还没测过真实的日文 PDF（编码/字体问题） → Day 6 验证

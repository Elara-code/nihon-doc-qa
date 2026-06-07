# 轻量镜像：不预下载模型，运行时由 sentence-transformers 按需拉取并缓存到挂载/容器卷。
# 优点：镜像 <2GB，构建快、推送快、HF Spaces 友好。
# 代价：首次启动需 1-2 分钟下载 bge-m3 + reranker（约 2.5GB）。

FROM python:3.11-slim

# 系统依赖：PyMuPDF 需要少量 C 库；ca-certificates 走 HTTPS 必备
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        ca-certificates \
        curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 让 Python 输出立即 flush，便于看 Streamlit 启动日志
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/app/.cache/huggingface \
    SENTENCE_TRANSFORMERS_HOME=/app/.cache/huggingface

# 先装依赖，利用 Docker 层缓存（依赖不变时这一层不重建）
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# 再复制源码
COPY src/ ./src/
COPY app.py ./
COPY .streamlit/ ./.streamlit/
COPY samples/ ./samples/

EXPOSE 8501

# Streamlit 需要监听 0.0.0.0 才能从容器外访问
# enableCORS / enableXsrfProtection 关掉，HF Spaces 反向代理下 XSRF 检查会
#   误拒上传请求（403）
# fileWatcherType=none 关掉文件监视器，避免 transformers vision 模块的误扫报错
CMD ["streamlit", "run", "app.py", \
     "--server.address=0.0.0.0", \
     "--server.port=8501", \
     "--server.headless=true", \
     "--server.enableCORS=false", \
     "--server.enableXsrfProtection=false", \
     "--server.fileWatcherType=none", \
     "--browser.gatherUsageStats=false"]

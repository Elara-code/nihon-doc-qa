"""集中读取 .env 配置。"""
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    llm_provider: str = os.getenv("LLM_PROVIDER", "deepseek")
    llm_api_key: str = os.getenv("LLM_API_KEY", "")
    llm_base_url: str = os.getenv("LLM_BASE_URL", "https://api.deepseek.com/v1")
    llm_model: str = os.getenv("LLM_MODEL", "deepseek-chat")

    embedding_model: str = os.getenv("EMBEDDING_MODEL", "BAAI/bge-m3")

    chroma_dir: str = os.getenv("CHROMA_DIR", "./chroma_db")
    chroma_collection: str = os.getenv("CHROMA_COLLECTION", "nihon_doc_qa")

    chunk_size: int = int(os.getenv("CHUNK_SIZE", "500"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "50"))
    top_k: int = int(os.getenv("TOP_K", "5"))

    # 检索模式：vector / hybrid / rerank
    #   vector = 仅向量；hybrid = 向量 + BM25（RRF 融合）；rerank = hybrid 后再用交叉编码器精排
    retrieval_mode: str = os.getenv("RETRIEVAL_MODE", "rerank")
    # 融合/精排前每路召回的候选数
    candidate_k: int = int(os.getenv("CANDIDATE_K", "20"))
    # RRF 融合常数（越大越平滑，经验值 60）
    rrf_k: int = int(os.getenv("RRF_K", "60"))
    # 重排序模型
    rerank_model: str = os.getenv("RERANK_MODEL", "BAAI/bge-reranker-v2-m3")


settings = Settings()

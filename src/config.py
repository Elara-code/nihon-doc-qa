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


settings = Settings()

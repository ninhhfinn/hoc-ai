"""Cau hinh toan app, doc tu bien moi truong hoac file .env.

Moi module khac phai lay cau hinh qua ham lay_cau_hinh(), khong duoc doc
os.environ truc tiep. Nho vay moi thiet lap deu co kieu va duoc kiem tra
ngay luc khoi dong thay vi hong am tham luc chay.
"""

from pathlib import Path
from typing import Literal

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Toan bo thiet lap cua app."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- LLM ---
    llm_provider: Literal["deepseek", "ollama", "fake"] = "fake"
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-v4-flash"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:7b"

    # --- Embedding ---
    embedding_model: str = "intfloat/multilingual-e5-base"
    embedding_device: Literal["cuda", "cpu"] = "cuda"

    # --- Luu tru ---
    data_dir: Path = Path("data")
    sqlite_path: Path = Path("data/hocai.db")
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "lessons"

    # --- Van hanh ---
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

    @model_validator(mode="after")
    def _kiem_tra_khoa_api(self) -> "Settings":
        if self.llm_provider == "deepseek" and not self.deepseek_api_key:
            raise ValueError(
                "Chon LLM_PROVIDER=deepseek thi phai dat DEEPSEEK_API_KEY trong file .env"
            )
        return self


def lay_cau_hinh() -> Settings:
    """Tra ve cau hinh doc tu moi truong hien tai."""
    return Settings()

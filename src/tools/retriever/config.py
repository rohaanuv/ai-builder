"""Configuration for the retriever."""

from __future__ import annotations

from pydantic import BaseModel, Field


class RetrieverConfig(BaseModel):
    """Configuration for the retriever."""

    provider: str = Field(
        default="faiss",
        description="Backend id (faiss/chroma/qdrant implemented in ai-builder)",
    )
    store_path: str = Field(default="data/vectorstore")
    collection_name: str = Field(default="default")
    top_k: int = Field(default=5, ge=1, le=100)
    embedding_model: str = Field(default="sentence-transformers/all-MiniLM-L6-v2")
    device: str = Field(default="cpu")

    chroma_host: str = "localhost"
    chroma_port: int = 8000
    qdrant_url: str = "http://localhost:6333"

    model_config = {"extra": "allow"}

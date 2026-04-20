"""Configuration for the vector store writer."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class VectorStoreConfig(BaseModel):
    """Configuration for the vector store."""

    provider: Literal["faiss", "chroma", "qdrant"] = Field(
        default="faiss", description="Vector database backend",
    )
    store_path: str = Field(default="data/vectorstore", description="Local path for index files")
    collection_name: str = Field(default="default", description="Collection / index name")

    chroma_host: str = Field(default="localhost", description="Chroma server host")
    chroma_port: int = Field(default=8000, description="Chroma server port")
    qdrant_url: str = Field(default="http://localhost:6333", description="Qdrant server URL")

    model_config = {"extra": "allow"}

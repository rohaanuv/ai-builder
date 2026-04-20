"""Configuration for sentence-transformers embeddings."""

from __future__ import annotations

from pydantic import BaseModel, Field

SUPPORTED_MODELS = {
    "sentence-transformers/all-MiniLM-L6-v2": {"dim": 384, "max_seq": 256},
    "sentence-transformers/all-mpnet-base-v2": {"dim": 768, "max_seq": 384},
    "BAAI/bge-small-en-v1.5": {"dim": 384, "max_seq": 512},
    "BAAI/bge-base-en-v1.5": {"dim": 768, "max_seq": 512},
    "BAAI/bge-m3": {"dim": 768, "max_seq": 512},
    "BAAI/bge-large-en-v1.5": {"dim": 1024, "max_seq": 512},
    "thenlper/gte-small": {"dim": 384, "max_seq": 512},
    "thenlper/gte-base": {"dim": 768, "max_seq": 512},
}


class EmbedderConfig(BaseModel):
    """Configuration for the embedding tool."""

    model_id: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        description="HuggingFace model identifier for embeddings",
    )
    batch_size: int = Field(default=64, ge=1, le=512, description="Texts per batch")
    device: str = Field(default="cpu", description="Device: cpu, cuda, mps")
    normalize: bool = Field(default=True, description="L2-normalize embeddings")

    model_config = {"extra": "allow"}

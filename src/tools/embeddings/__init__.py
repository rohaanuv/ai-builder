"""
Embeddings — sentence-transformers Embedder, config, presets, and scaffold registry.

Input:  ToolInput(data=[{text, ...}])    -> list of chunk dicts
Output: EmbedderOutput(data=[{text, embedding, ...}])  -> chunks with embeddings added

Requires: sentence-transformers (optional dep; see per-model extras in rag scaffold).
"""

from __future__ import annotations

from .config import EmbedderConfig, SUPPORTED_MODELS
from .main import Embedder, EmbedderOutput, tool
from .registry import (
    EMBEDDING_EXTRA_BY_MODEL,
    EMBEDDING_PACKAGES_BY_MODEL,
    extra_name_for_model,
    packages_for_model,
)

from . import (
    bge_base_en_v15,
    bge_large_en_v15,
    bge_m3,
    bge_small_en_v15,
    gte_base,
    gte_small,
    minilm_l6_v2,
    mpnet_base_v2,
)

TOOLS_BY_MODEL_ID: dict[str, Embedder] = {
    minilm_l6_v2.MODEL_ID: minilm_l6_v2.tool,
    mpnet_base_v2.MODEL_ID: mpnet_base_v2.tool,
    bge_small_en_v15.MODEL_ID: bge_small_en_v15.tool,
    bge_base_en_v15.MODEL_ID: bge_base_en_v15.tool,
    bge_m3.MODEL_ID: bge_m3.tool,
    bge_large_en_v15.MODEL_ID: bge_large_en_v15.tool,
    gte_small.MODEL_ID: gte_small.tool,
    gte_base.MODEL_ID: gte_base.tool,
}


def get_preset_embedder(model_id: str) -> Embedder:
    """Return the preset Embedder for a supported MODEL_ID."""
    if model_id not in TOOLS_BY_MODEL_ID:
        raise KeyError(f"Unsupported embedding model_id: {model_id!r}")
    return TOOLS_BY_MODEL_ID[model_id]


__all__ = [
    "EMBEDDING_EXTRA_BY_MODEL",
    "EMBEDDING_PACKAGES_BY_MODEL",
    "Embedder",
    "EmbedderConfig",
    "EmbedderOutput",
    "SUPPORTED_MODELS",
    "TOOLS_BY_MODEL_ID",
    "extra_name_for_model",
    "get_preset_embedder",
    "packages_for_model",
    "tool",
]

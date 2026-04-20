"""
embedder — Vector embedding tool.

Input:  ToolInput(data=[{text, ...}])    -> list of chunk dicts
Output: EmbedderOutput(data=[{text, embedding, ...}])  -> chunks with embeddings added

Requires: sentence-transformers (optional dep)
"""

from ai_builder.tools.embedder.config import EmbedderConfig, SUPPORTED_MODELS
from ai_builder.tools.embedder.main import Embedder, EmbedderOutput

__all__ = ["Embedder", "EmbedderConfig", "EmbedderOutput", "SUPPORTED_MODELS"]

"""Preset Embedder for BAAI/bge-m3."""

from .config import EmbedderConfig
from .main import Embedder

MODEL_ID = "BAAI/bge-m3"

tool = Embedder(EmbedderConfig(model_id=MODEL_ID))

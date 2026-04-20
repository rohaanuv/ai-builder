"""Preset Embedder for BAAI/bge-small-en-v1.5."""

from .config import EmbedderConfig
from .main import Embedder

MODEL_ID = "BAAI/bge-small-en-v1.5"

tool = Embedder(EmbedderConfig(model_id=MODEL_ID))

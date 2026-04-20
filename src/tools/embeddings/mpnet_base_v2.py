"""Preset Embedder for sentence-transformers/all-mpnet-base-v2."""

from .config import EmbedderConfig
from .main import Embedder

MODEL_ID = "sentence-transformers/all-mpnet-base-v2"

tool = Embedder(EmbedderConfig(model_id=MODEL_ID))

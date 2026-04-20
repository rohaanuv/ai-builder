"""Preset Embedder for thenlper/gte-small."""

from .config import EmbedderConfig
from .main import Embedder

MODEL_ID = "thenlper/gte-small"

tool = Embedder(EmbedderConfig(model_id=MODEL_ID))

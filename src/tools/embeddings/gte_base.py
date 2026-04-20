"""Preset Embedder for thenlper/gte-base."""

from .config import EmbedderConfig
from .main import Embedder

MODEL_ID = "thenlper/gte-base"

tool = Embedder(EmbedderConfig(model_id=MODEL_ID))

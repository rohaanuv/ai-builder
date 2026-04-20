"""Embedder — generates vector embeddings for text chunks."""

from __future__ import annotations

import logging
from typing import Any

from pydantic import Field

from ai_builder.core.tool import BaseTool, ToolInput, ToolOutput
from .config import EmbedderConfig, SUPPORTED_MODELS

logger = logging.getLogger(__name__)


class EmbedderOutput(ToolOutput):
    """Output: chunks with 'embedding' field added."""

    data: list[dict[str, Any]] = Field(default_factory=list)


class Embedder(BaseTool[ToolInput, EmbedderOutput]):
    """
    Generate vector embeddings for text chunks using sentence-transformers.
    Supports batched encoding and multiple pre-configured models.
    """

    name = "embedder"
    description = "Generate vector embeddings using sentence-transformers models"
    version = "1.0.0"

    def __init__(self, config: EmbedderConfig | None = None) -> None:
        self.config = config or EmbedderConfig()
        self._model: Any = None

    @property
    def model(self) -> Any:
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.config.model_id, device=self.config.device)
        return self._model

    def execute(self, inp: ToolInput) -> EmbedderOutput:
        chunks = inp.data if isinstance(inp.data, list) else []
        if not chunks:
            return EmbedderOutput(data=[], success=False, error="No chunks to embed")

        texts = [c.get("text", "") for c in chunks]

        try:
            embeddings = self._encode_batched(texts)
        except Exception as exc:
            return EmbedderOutput(data=[], success=False, error=f"Encoding failed: {exc}")

        dimension = len(embeddings[0]) if embeddings else 0
        for chunk, emb in zip(chunks, embeddings):
            chunk["embedding"] = emb

        return EmbedderOutput(
            data=chunks,
            metadata={
                **inp.metadata,
                "model": self.config.model_id,
                "dimension": dimension,
                "embedded_count": len(embeddings),
            },
        )

    def _encode_batched(self, texts: list[str]) -> list[list[float]]:
        all_embs: list[list[float]] = []
        bs = self.config.batch_size
        for i in range(0, len(texts), bs):
            batch = texts[i : i + bs]
            embs = self.model.encode(
                batch, normalize_embeddings=self.config.normalize, show_progress_bar=False,
            )
            all_embs.extend(embs.tolist())
        return all_embs

    @classmethod
    def list_models(cls) -> dict:
        return SUPPORTED_MODELS


tool = Embedder()

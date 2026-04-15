"""Retriever — searches the vector store for relevant chunks."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field

from ai_builder.core.tool import BaseTool, ToolInput, ToolOutput

logger = logging.getLogger(__name__)


class RetrieverConfig(BaseModel):
    """Configuration for the retriever."""

    provider: Literal["faiss", "chroma", "qdrant"] = Field(default="faiss")
    store_path: str = Field(default="data/vectorstore")
    collection_name: str = Field(default="default")
    top_k: int = Field(default=5, ge=1, le=100)
    embedding_model: str = Field(default="sentence-transformers/all-MiniLM-L6-v2")
    device: str = Field(default="cpu")

    chroma_host: str = "localhost"
    chroma_port: int = 8000
    qdrant_url: str = "http://localhost:6333"

    model_config = {"extra": "allow"}


class RetrieverInput(ToolInput):
    """Input: query text in .data, optional top_k in .metadata."""

    data: str = Field(default="", description="Query text")


class RetrieverOutput(ToolOutput):
    """Output: ranked list of {text, source, score} dicts."""

    data: list[dict[str, Any]] = Field(default_factory=list)


class Retriever(BaseTool[RetrieverInput, RetrieverOutput]):
    """
    Retrieve relevant chunks from a vector store by embedding a query
    and performing similarity search. Supports FAISS, Chroma, Qdrant.
    """

    name = "retriever"
    description = "Retrieve relevant document chunks via vector similarity search"
    version = "1.0.0"

    def __init__(self, config: RetrieverConfig | None = None) -> None:
        self.config = config or RetrieverConfig()
        self._encoder: Any = None

    @property
    def encoder(self) -> Any:
        if self._encoder is None:
            from sentence_transformers import SentenceTransformer
            self._encoder = SentenceTransformer(self.config.embedding_model, device=self.config.device)
        return self._encoder

    def execute(self, inp: RetrieverInput) -> RetrieverOutput:
        query = inp.data if isinstance(inp.data, str) else ""
        if not query:
            return RetrieverOutput(data=[], success=False, error="No query text")

        top_k = inp.metadata.get("top_k", self.config.top_k)
        provider = self.config.provider

        try:
            query_emb = self.encoder.encode([query], normalize_embeddings=True)[0].tolist()
        except Exception as exc:
            return RetrieverOutput(data=[], success=False, error=f"Encoding failed: {exc}")

        if provider == "faiss":
            return self._search_faiss(query_emb, top_k, inp.metadata, query)
        elif provider == "chroma":
            return self._search_chroma(query, top_k, inp.metadata)
        elif provider == "qdrant":
            return self._search_qdrant(query_emb, top_k, inp.metadata, query)
        else:
            return RetrieverOutput(data=[], success=False, error=f"Unknown provider: {provider}")

    def _search_faiss(self, emb: list[float], k: int, meta: dict, query: str) -> RetrieverOutput:
        import numpy as np
        import faiss

        store = Path(self.config.store_path)
        idx_file = store / f"{self.config.collection_name}.faiss"
        meta_file = store / f"{self.config.collection_name}.meta.json"

        if not idx_file.exists():
            return RetrieverOutput(data=[], success=False, error="No FAISS index. Run ingest first.")

        index = faiss.read_index(str(idx_file))
        metadata = json.loads(meta_file.read_text()) if meta_file.exists() else []

        vec = np.array([emb], dtype="float32")
        scores, indices = index.search(vec, min(k, index.ntotal))

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0 or idx >= len(metadata):
                continue
            entry = metadata[idx].copy()
            entry["score"] = float(score)
            results.append(entry)

        return RetrieverOutput(
            data=results,
            metadata={**meta, "query": query, "provider": "faiss", "sources": results},
        )

    def _search_chroma(self, query: str, k: int, meta: dict) -> RetrieverOutput:
        import chromadb

        client = chromadb.HttpClient(host=self.config.chroma_host, port=self.config.chroma_port)
        col = client.get_collection(self.config.collection_name)
        res = col.query(query_texts=[query], n_results=k)

        results = []
        for i, doc in enumerate(res["documents"][0]):
            results.append({
                "text": doc,
                "source": res["metadatas"][0][i].get("source", ""),
                "score": 1.0 - (res["distances"][0][i] if res.get("distances") else 0),
            })

        return RetrieverOutput(
            data=results,
            metadata={**meta, "query": query, "provider": "chroma", "sources": results},
        )

    def _search_qdrant(self, emb: list[float], k: int, meta: dict, query: str) -> RetrieverOutput:
        from qdrant_client import QdrantClient

        client = QdrantClient(url=self.config.qdrant_url)
        hits = client.search(self.config.collection_name, query_vector=emb, limit=k)

        results = [
            {"text": h.payload.get("text", ""), "source": h.payload.get("source", ""),
             "score": h.score}
            for h in hits
        ]

        return RetrieverOutput(
            data=results,
            metadata={**meta, "query": query, "provider": "qdrant", "sources": results},
        )

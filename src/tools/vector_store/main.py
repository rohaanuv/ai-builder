"""VectorStoreWriter — indexes embeddings with pluggable backends (FAISS, Chroma, Qdrant)."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from ai_builder.core.tool import BaseTool, ToolInput, ToolOutput
from ai_builder.tools.vector_store.config import VectorStoreConfig

logger = logging.getLogger(__name__)


class VectorStoreWriter(BaseTool[ToolInput, ToolOutput]):
    """
    Write embeddings to a vector store. Supports FAISS (local),
    Chroma (local/remote), and Qdrant (remote).
    """

    name = "vector_store"
    description = "Index embeddings into a vector database (FAISS, Chroma, Qdrant)"
    version = "1.0.0"

    def __init__(self, config: VectorStoreConfig | None = None) -> None:
        self.config = config or VectorStoreConfig()

    def execute(self, inp: ToolInput) -> ToolOutput:
        chunks = inp.data if isinstance(inp.data, list) else []
        if not chunks:
            return ToolOutput(data=None, success=False, error="No chunks to store")

        provider = self.config.provider
        if provider == "faiss":
            return self._write_faiss(chunks, inp.metadata)
        elif provider == "chroma":
            return self._write_chroma(chunks, inp.metadata)
        elif provider == "qdrant":
            return self._write_qdrant(chunks, inp.metadata)
        else:
            return ToolOutput(data=None, success=False, error=f"Unknown provider: {provider}")

    def _write_faiss(self, chunks: list[dict], meta: dict) -> ToolOutput:
        import numpy as np
        import faiss

        embeddings = np.array([c["embedding"] for c in chunks], dtype="float32")
        dim = embeddings.shape[1]

        store = Path(self.config.store_path)
        store.mkdir(parents=True, exist_ok=True)
        idx_file = store / f"{self.config.collection_name}.faiss"
        meta_file = store / f"{self.config.collection_name}.meta.json"

        index = faiss.read_index(str(idx_file)) if idx_file.exists() else faiss.IndexFlatIP(dim)
        index.add(embeddings)
        faiss.write_index(index, str(idx_file))

        metadata: list[dict] = json.loads(meta_file.read_text()) if meta_file.exists() else []
        for c in chunks:
            metadata.append({
                "text": c.get("text", ""),
                "source": c.get("source", ""),
                "chunk_index": c.get("chunk_index", 0),
                "chunk_id": c.get("chunk_id", ""),
            })
        meta_file.write_text(json.dumps(metadata))

        return ToolOutput(
            data={"indexed": len(chunks), "total": index.ntotal, "provider": "faiss"},
            metadata={**meta, "store_path": str(store)},
        )

    def _write_chroma(self, chunks: list[dict], meta: dict) -> ToolOutput:
        import chromadb

        client = chromadb.HttpClient(host=self.config.chroma_host, port=self.config.chroma_port)
        collection = client.get_or_create_collection(self.config.collection_name)

        ids = [c.get("chunk_id", f"chunk-{i}") for i, c in enumerate(chunks)]
        embeddings = [c["embedding"] for c in chunks]
        documents = [c.get("text", "") for c in chunks]
        metadatas = [{"source": c.get("source", ""), "chunk_index": c.get("chunk_index", 0)}
                     for c in chunks]

        collection.add(ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas)

        return ToolOutput(
            data={"indexed": len(chunks), "total": collection.count(), "provider": "chroma"},
            metadata=meta,
        )

    def _write_qdrant(self, chunks: list[dict], meta: dict) -> ToolOutput:
        from qdrant_client import QdrantClient
        from qdrant_client.models import PointStruct, VectorParams, Distance

        client = QdrantClient(url=self.config.qdrant_url)
        dim = len(chunks[0]["embedding"])

        try:
            client.get_collection(self.config.collection_name)
        except Exception:
            client.create_collection(
                self.config.collection_name,
                vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
            )

        points = [
            PointStruct(
                id=i,
                vector=c["embedding"],
                payload={"text": c.get("text", ""), "source": c.get("source", ""),
                         "chunk_index": c.get("chunk_index", 0)},
            )
            for i, c in enumerate(chunks)
        ]
        client.upsert(self.config.collection_name, points)

        info = client.get_collection(self.config.collection_name)
        return ToolOutput(
            data={"indexed": len(chunks), "total": info.points_count, "provider": "qdrant"},
            metadata=meta,
        )


tool = VectorStoreWriter()

"""FAISS vector store tool instance (provider=faiss)."""

from ai_builder.tools.vector_store import VectorStoreWriter
from ai_builder.tools.vector_store.config import VectorStoreConfig

tool = VectorStoreWriter(VectorStoreConfig(provider="faiss"))

"""
vector_store — Vector database writer tool.

Input:  ToolInput(data=[{text, embedding, ...}])   -> chunks with embeddings
Output: ToolOutput(data={indexed, total, provider}) -> index stats

Requires: faiss-cpu / chromadb / qdrant-client (optional deps)
"""

from ai_builder.tools.vector_store.config import VectorStoreConfig
from ai_builder.tools.vector_store.main import VectorStoreWriter

__all__ = ["VectorStoreWriter", "VectorStoreConfig"]

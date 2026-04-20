"""
retriever — Vector similarity search tool.

Input:  RetrieverInput(data="query text")              -> search query
Output: RetrieverOutput(data=[{text, source, score}])  -> ranked results

Requires: sentence-transformers + faiss-cpu/chromadb/qdrant-client (optional deps)
"""

from ai_builder.tools.retriever.config import RetrieverConfig
from ai_builder.tools.retriever.main import Retriever, RetrieverInput, RetrieverOutput

__all__ = ["Retriever", "RetrieverConfig", "RetrieverInput", "RetrieverOutput"]

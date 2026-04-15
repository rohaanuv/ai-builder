"""
ai_builder.tools — built-in reusable tool library.

These tools follow the BaseTool[Input, Output] pattern and can be composed
via the | operator into pipelines.

Usage:
    from ai_builder.tools import DocumentLoader, TextSplitter, Embedder, VectorStore, Retriever

    ingest_pipeline = DocumentLoader() | TextSplitter() | Embedder() | VectorStore()
    result = ingest_pipeline.run(ToolInput(data="./docs/"))
"""

from ai_builder.tools.loader import DocumentLoader, LoaderConfig, LoaderInput, LoaderOutput
from ai_builder.tools.splitter import TextSplitter, SplitterConfig, SplitterOutput
from ai_builder.tools.embedder import Embedder, EmbedderConfig, EmbedderOutput
from ai_builder.tools.vector_store import VectorStoreWriter, VectorStoreConfig
from ai_builder.tools.retriever import Retriever, RetrieverConfig, RetrieverInput, RetrieverOutput
from ai_builder.tools.llm import LLMTool, LLMConfig, LLMInput, LLMOutput
from ai_builder.tools.web_search import WebSearchTool, WebSearchInput, WebSearchOutput

__all__ = [
    "DocumentLoader", "LoaderConfig", "LoaderInput", "LoaderOutput",
    "TextSplitter", "SplitterConfig", "SplitterOutput",
    "Embedder", "EmbedderConfig", "EmbedderOutput",
    "VectorStoreWriter", "VectorStoreConfig",
    "Retriever", "RetrieverConfig", "RetrieverInput", "RetrieverOutput",
    "LLMTool", "LLMConfig", "LLMInput", "LLMOutput",
    "WebSearchTool", "WebSearchInput", "WebSearchOutput",
]

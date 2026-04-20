"""
ai_builder.tools — built-in reusable tool library.

Document loading lives under ``document_loader`` (shared ``common`` + ``loader_*`` packages):

    document_loader/     DocumentLoader, LoaderInput → LoaderOutput (umbrella + shared types)
    document_loader/loader_pdf/, loader_word/, …      One format family per package

Usage:

    from ai_builder.tools.document_loader import loader_pdf
    from ai_builder.tools.document_loader.loader_pdf import PdfLoader

    from ai_builder.tools import DocumentLoader, TextSplitter, Embedder

    ingest_pipeline = DocumentLoader() | TextSplitter() | Embedder()
    result = ingest_pipeline.run(ToolInput(data="./docs/"))
"""

from ai_builder.tools.document_loader import DocumentLoader, LoaderConfig, LoaderInput, LoaderOutput
from ai_builder.tools.document_loader.loader_epub import EpubLoader
from ai_builder.tools.document_loader.loader_html import HtmlLoader
from ai_builder.tools.document_loader.loader_json import JsonLoader
from ai_builder.tools.document_loader.loader_pdf import PdfLoader
from ai_builder.tools.document_loader.loader_rtf import RtfLoader
from ai_builder.tools.document_loader.loader_slides import SlidesLoader
from ai_builder.tools.document_loader.loader_spreadsheet import SpreadsheetLoader
from ai_builder.tools.document_loader.loader_text import PlainTextLoader
from ai_builder.tools.document_loader.loader_word import WordLoader
from ai_builder.tools.document_loader.loader_xml import XmlLoader
from ai_builder.tools.embeddings import (
    Embedder,
    EmbedderConfig,
    EmbedderOutput,
    SUPPORTED_MODELS,
)
from ai_builder.tools.llm import (
    LLMConfig,
    LLMInput,
    LLMOutput,
    LLMTool,
    connectAnthropic,
    connectAzure,
    connectBedrock,
    connectOllama,
    connectOpenAI,
    connectSelfHostedLLM,
    connect_anthropic,
    connect_azure,
    connect_bedrock,
    connect_ollama,
    connect_openai,
    connect_self_hosted_llm,
)
from ai_builder.tools.retriever import Retriever, RetrieverConfig, RetrieverInput, RetrieverOutput
from ai_builder.tools.splitter import SplitterConfig, SplitterOutput, TextSplitter
from ai_builder.tools.data_source import (
    AzureBlobDataSource,
    GcsDataSource,
    LocalFilesystemDataSource,
    S3DataSource,
)
from ai_builder.tools.vector_store import VectorStoreConfig, VectorStoreWriter
from ai_builder.tools.web_search import WebSearchInput, WebSearchOutput, WebSearchTool

__all__ = [
    "DocumentLoader",
    "LoaderConfig",
    "LoaderInput",
    "LoaderOutput",
    "PdfLoader",
    "PlainTextLoader",
    "SpreadsheetLoader",
    "WordLoader",
    "RtfLoader",
    "SlidesLoader",
    "JsonLoader",
    "HtmlLoader",
    "XmlLoader",
    "EpubLoader",
    "TextSplitter",
    "SplitterConfig",
    "SplitterOutput",
    "Embedder",
    "EmbedderConfig",
    "EmbedderOutput",
    "SUPPORTED_MODELS",
    "VectorStoreWriter",
    "VectorStoreConfig",
    "Retriever",
    "RetrieverConfig",
    "RetrieverInput",
    "RetrieverOutput",
    "LLMTool",
    "LLMConfig",
    "LLMInput",
    "LLMOutput",
    "connect_openai",
    "connectOpenAI",
    "connect_anthropic",
    "connectAnthropic",
    "connect_ollama",
    "connectOllama",
    "connect_self_hosted_llm",
    "connectSelfHostedLLM",
    "connect_bedrock",
    "connectBedrock",
    "connect_azure",
    "connectAzure",
    "WebSearchTool",
    "WebSearchInput",
    "WebSearchOutput",
    "LocalFilesystemDataSource",
    "S3DataSource",
    "AzureBlobDataSource",
    "GcsDataSource",
]

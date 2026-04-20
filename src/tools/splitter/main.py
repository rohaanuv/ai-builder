"""TextSplitter — chunks documents with configurable size and overlap."""

from __future__ import annotations

import hashlib
import logging
from typing import Any

from pydantic import Field

from ai_builder.core.tool import BaseTool, ToolInput, ToolOutput
from ai_builder.tools.splitter.config import SplitterConfig

logger = logging.getLogger(__name__)


class SplitterOutput(ToolOutput):
    """Output: list of chunk dicts with text, source, chunk_index, chunk_id."""

    data: list[dict[str, Any]] = Field(default_factory=list)


class TextSplitter(BaseTool[ToolInput, SplitterOutput]):
    """
    Split documents into overlapping chunks using recursive character splitting.
    Generates deterministic chunk IDs for incremental updates.
    """

    name = "splitter"
    description = "Split documents into overlapping chunks with metadata and IDs"
    version = "1.0.0"

    def __init__(self, config: SplitterConfig | None = None) -> None:
        self.config = config or SplitterConfig()

    def execute(self, inp: ToolInput) -> SplitterOutput:
        docs = inp.data if isinstance(inp.data, list) else []
        if not docs:
            return SplitterOutput(data=[], success=False, error="No documents to split")

        all_chunks: list[dict[str, Any]] = []
        for doc in docs:
            text = doc.get("text", "")
            source = doc.get("source", "unknown")
            if not text:
                continue

            pieces = self._recursive_split(text)
            for i, piece in enumerate(pieces):
                chunk: dict[str, Any] = {
                    "text": piece,
                    "source": source,
                    "chunk_index": i,
                    "char_count": len(piece),
                }
                if self.config.add_chunk_ids:
                    chunk["chunk_id"] = self._make_id(source, i, piece)
                all_chunks.append(chunk)

        return SplitterOutput(
            data=all_chunks,
            metadata={**inp.metadata, "chunk_count": len(all_chunks)},
        )

    def _recursive_split(self, text: str) -> list[str]:
        size = self.config.chunk_size
        overlap = self.config.chunk_overlap
        seps = self.config.separators

        try:
            from langchain_text_splitters import RecursiveCharacterTextSplitter

            splitter = RecursiveCharacterTextSplitter(
                chunk_size=size, chunk_overlap=overlap, separators=seps,
            )
            return splitter.split_text(text)
        except ImportError:
            pass

        chunks = []
        start = 0
        while start < len(text):
            end = start + size
            chunks.append(text[start:end])
            start = end - overlap
        return chunks

    @staticmethod
    def _make_id(source: str, index: int, text: str) -> str:
        content = f"{source}::{index}::{text[:200]}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]


tool = TextSplitter()

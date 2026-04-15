"""Configuration for the text splitter."""

from __future__ import annotations

from pydantic import BaseModel, Field


class SplitterConfig(BaseModel):
    """Configuration for text splitting."""

    chunk_size: int = Field(default=1000, ge=100, le=10_000, description="Characters per chunk")
    chunk_overlap: int = Field(default=200, ge=0, le=2000, description="Overlap between chunks")
    separators: list[str] = Field(
        default=["\n\n", "\n", ". ", " ", ""],
        description="Split separators in priority order",
    )
    add_chunk_ids: bool = Field(default=True, description="Generate deterministic chunk IDs")

    model_config = {"extra": "allow"}

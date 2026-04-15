"""Configuration for the document loader."""

from __future__ import annotations

from pydantic import BaseModel, Field


class LoaderConfig(BaseModel):
    """Configuration for the document loader."""

    source_dir: str = Field(default="data/raw", description="Directory to load documents from")
    supported_formats: list[str] = Field(
        default=[
            ".txt", ".md", ".csv", ".json", ".xml",
            ".pdf", ".docx", ".doc", ".pptx",
            ".html", ".htm", ".rtf", ".xlsx",
        ],
        description="File extensions to process",
    )
    recursive: bool = Field(default=True, description="Recurse into subdirectories")

    model_config = {"extra": "allow"}

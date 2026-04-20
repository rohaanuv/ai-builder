"""Umbrella document loader — all registered format extractors."""

from __future__ import annotations

from pydantic import Field

from ai_builder.core.tool import BaseTool

from ai_builder.tools.document_loader.common.extract import DEFAULT_UMBRELLA_FORMATS
from ai_builder.tools.document_loader.common.runner import run_loader
from ai_builder.tools.document_loader.common.schemas import LoaderConfig as _BaseLoaderConfig
from ai_builder.tools.document_loader.common.schemas import LoaderInput, LoaderOutput


class LoaderConfig(_BaseLoaderConfig):
    """Defaults to every extension implemented in ``common.extract``."""

    supported_formats: list[str] = Field(
        default_factory=lambda: list(DEFAULT_UMBRELLA_FORMATS),
        description="File extensions to process",
    )


class DocumentLoader(BaseTool[LoaderInput, LoaderOutput]):
    """
    Load and extract text from documents (all supported extensions).

    For one format family, use e.g. :class:`~ai_builder.tools.document_loader.loader_pdf.main.PdfLoader`.
    """

    name = "loader"
    description = "Load documents from filesystem with format-specific text extraction"
    version = "2.0.0"

    def __init__(self, config: LoaderConfig | None = None) -> None:
        self.config = config or LoaderConfig()

    def execute(self, inp: LoaderInput) -> LoaderOutput:
        allowed = {s.lower() for s in self.config.supported_formats}
        return run_loader(inp, self.config, allowed_suffixes=allowed)


tool = DocumentLoader()

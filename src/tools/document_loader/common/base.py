"""Base class for single-format-family document loaders."""

from __future__ import annotations

from typing import ClassVar

from ai_builder.core.tool import BaseTool

from .runner import run_loader
from .schemas import LoaderConfig, LoaderInput, LoaderOutput


class FormatLoader(BaseTool[LoaderInput, LoaderOutput]):
    """Load and extract text for one family of file extensions."""

    name = "format-loader"
    description = "Load documents for specific file types"
    version = "1.0.0"
    suffixes: ClassVar[tuple[str, ...]] = ()

    def __init__(self, config: LoaderConfig | None = None) -> None:
        allowed = frozenset(self.suffixes)
        if config is None:
            self.config = LoaderConfig(supported_formats=sorted(allowed))
        else:
            merged = LoaderConfig(**{**config.model_dump(), "supported_formats": sorted(allowed)})
            self.config = merged

    def execute(self, inp: LoaderInput) -> LoaderOutput:
        return run_loader(inp, self.config, allowed_suffixes=set(self.suffixes))

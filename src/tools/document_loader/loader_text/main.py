"""Extract text from .txt and .md files."""

from typing import ClassVar

from ..common import FormatLoader


class PlainTextLoader(FormatLoader):
    """Load UTF-8 plain text and Markdown files."""

    name = "loader-text"
    description = "Load plain text (.txt) and Markdown (.md)"
    version = "1.0.0"
    suffixes: ClassVar[tuple[str, ...]] = (".txt", ".md")


tool = PlainTextLoader()

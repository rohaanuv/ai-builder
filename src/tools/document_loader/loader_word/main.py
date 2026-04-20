"""Extract text from Word .doc/.docx and templates .dot/.dotx."""

from typing import ClassVar

from ..common import FormatLoader


class WordLoader(FormatLoader):
    """Load Word binary/XML documents and legacy .doc."""

    name = "loader-word"
    description = "Load Word documents: .doc, .docx, .dot, .dotx"
    version = "1.0.0"
    suffixes: ClassVar[tuple[str, ...]] = (".doc", ".docx", ".dot", ".dotx")


tool = WordLoader()

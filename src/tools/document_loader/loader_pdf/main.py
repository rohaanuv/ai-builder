"""Extract text from PDF files (.pdf)."""

from typing import ClassVar

from ..common import FormatLoader


class PdfLoader(FormatLoader):
    """Load and extract text from PDF documents."""

    name = "loader-pdf"
    description = "Load PDF documents and extract text (pdfplumber)"
    version = "1.0.0"
    suffixes: ClassVar[tuple[str, ...]] = (".pdf",)


tool = PdfLoader()

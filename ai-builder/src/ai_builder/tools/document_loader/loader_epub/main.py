"""Extract text from EPUB ebooks."""

from typing import ClassVar

from ..common import FormatLoader


class EpubLoader(FormatLoader):
    """Load EPUB publications and extract HTML body text."""

    name = "loader-epub"
    description = "Load EPUB ebooks (ebooklib)"
    version = "1.0.0"
    suffixes: ClassVar[tuple[str, ...]] = (".epub",)


tool = EpubLoader()

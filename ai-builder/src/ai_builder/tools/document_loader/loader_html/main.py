"""Extract visible text from HTML and HTM files."""

from typing import ClassVar

from ..common import FormatLoader


class HtmlLoader(FormatLoader):
    """Load HTML and strip tags to text (BeautifulSoup)."""

    name = "loader-html"
    description = "Load HTML documents (.html, .htm)"
    version = "1.0.0"
    suffixes: ClassVar[tuple[str, ...]] = (".html", ".htm")


tool = HtmlLoader()

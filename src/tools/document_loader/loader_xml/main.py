"""Extract text nodes from XML files."""

from typing import ClassVar

from ..common import FormatLoader


class XmlLoader(FormatLoader):
    """Load XML and concatenate text content."""

    name = "loader-xml"
    description = "Load XML documents"
    version = "1.0.0"
    suffixes: ClassVar[tuple[str, ...]] = (".xml",)


tool = XmlLoader()

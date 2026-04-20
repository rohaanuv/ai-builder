"""Extract text from RTF files."""

from typing import ClassVar

from ..common import FormatLoader


class RtfLoader(FormatLoader):
    """Load RTF and strip formatting to plain text."""

    name = "loader-rtf"
    description = "Load RTF documents (striprtf)"
    version = "1.0.0"
    suffixes: ClassVar[tuple[str, ...]] = (".rtf",)


tool = RtfLoader()

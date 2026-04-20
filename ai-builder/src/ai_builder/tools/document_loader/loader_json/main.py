"""Extract JSON as indented text for downstream chunking."""

from typing import ClassVar

from ..common import FormatLoader


class JsonLoader(FormatLoader):
    """Load JSON files (pretty-printed string form)."""

    name = "loader-json"
    description = "Load JSON documents"
    version = "1.0.0"
    suffixes: ClassVar[tuple[str, ...]] = (".json",)


tool = JsonLoader()

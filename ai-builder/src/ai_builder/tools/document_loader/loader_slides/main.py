"""Extract text from PowerPoint .pptx (and surface clear errors for legacy .ppt)."""

from typing import ClassVar

from ..common import FormatLoader


class SlidesLoader(FormatLoader):
    """Load presentation decks; .pptx is fully supported."""

    name = "loader-slides"
    description = "Load PowerPoint .pptx slides (legacy .ppt is not extracted in-process)"
    version = "1.0.0"
    suffixes: ClassVar[tuple[str, ...]] = (".pptx", ".ppt")


tool = SlidesLoader()

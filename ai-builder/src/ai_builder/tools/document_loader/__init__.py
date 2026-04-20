"""Document loaders — shared ``common`` helpers plus one package per format family.

Import format submodules::

    from ai_builder.tools.document_loader import loader_pdf
    from ai_builder.tools.document_loader.loader_pdf import PdfLoader

The umbrella :class:`DocumentLoader` loads every supported extension (same as before).
"""

from ai_builder.tools.document_loader.common import FormatLoader
from ai_builder.tools.document_loader.common.schemas import LoaderInput, LoaderOutput
from ai_builder.tools.document_loader.umbrella import DocumentLoader, LoaderConfig

from . import loader_epub
from . import loader_html
from . import loader_json
from . import loader_pdf
from . import loader_rtf
from . import loader_slides
from . import loader_spreadsheet
from . import loader_text
from . import loader_word
from . import loader_xml

__all__ = [
    "DocumentLoader",
    "LoaderConfig",
    "LoaderInput",
    "LoaderOutput",
    "FormatLoader",
    "loader_epub",
    "loader_html",
    "loader_json",
    "loader_pdf",
    "loader_rtf",
    "loader_slides",
    "loader_spreadsheet",
    "loader_text",
    "loader_word",
    "loader_xml",
]

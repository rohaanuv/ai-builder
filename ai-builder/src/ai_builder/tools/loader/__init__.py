"""
loader — Document loading tool.

Input:  LoaderInput(data="path/to/dir")    -> directory or file path
Output: LoaderOutput(data=[...])           -> list of {text, source, filename, format, chars}

Supported formats: TXT, MD, CSV, JSON, XML (stdlib), PDF, DOCX, DOC,
PPTX, HTML, HTM, RTF, XLSX (lazy-loaded optional deps).
"""

from ai_builder.tools.loader.config import LoaderConfig
from ai_builder.tools.loader.main import DocumentLoader, LoaderInput, LoaderOutput

__all__ = ["DocumentLoader", "LoaderConfig", "LoaderInput", "LoaderOutput"]

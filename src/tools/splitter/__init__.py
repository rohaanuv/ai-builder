"""
splitter — Text chunking tool.

Input:  ToolInput(data=[{text, source, ...}])    -> list of document dicts
Output: SplitterOutput(data=[{text, source, chunk_index, chunk_id, ...}])
"""

from ai_builder.tools.splitter.config import SplitterConfig
from ai_builder.tools.splitter.main import TextSplitter, SplitterOutput

__all__ = ["TextSplitter", "SplitterConfig", "SplitterOutput"]

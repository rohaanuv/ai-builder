"""
web_search — Web search tool.

Input:  WebSearchInput(data="search query")
Output: WebSearchOutput(data=[{title, url, content, score}])

Requires: tavily-python (optional dep)
"""

from ai_builder.tools.web_search.config import WebSearchConfig
from ai_builder.tools.web_search.main import WebSearchTool, WebSearchInput, WebSearchOutput

__all__ = ["WebSearchTool", "WebSearchConfig", "WebSearchInput", "WebSearchOutput"]

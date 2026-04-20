"""
llm — Language model text generation and provider connectors.

Input:  ``LLMInput(data="prompt")``  (optional ``metadata['context']`` for RAG)  
Output: ``LLMOutput(data="...")``

Use project-scoped imports in generated apps (see RAG template ``src/tools/``)::

    from tools.llm import connect_openai, connect_azure
    from tools.document_loader import loader_rtf
"""

from ai_builder.tools.llm.config import LLMConfig, Provider
from ai_builder.tools.llm.connectors import (
    connectAnthropic,
    connectAzure,
    connectBedrock,
    connectOllama,
    connectOpenAI,
    connectSelfHostedLLM,
    connect_anthropic,
    connect_azure,
    connect_bedrock,
    connect_ollama,
    connect_openai,
    connect_self_hosted_llm,
)
from ai_builder.tools.llm.tool import LLMTool, tool
from ai_builder.tools.llm.types import LLMInput, LLMOutput

__all__ = [
    "LLMConfig",
    "LLMInput",
    "LLMOutput",
    "LLMTool",
    "Provider",
    "connect_anthropic",
    "connect_azure",
    "connect_bedrock",
    "connect_ollama",
    "connect_openai",
    "connect_self_hosted_llm",
    "connectAnthropic",
    "connectAzure",
    "connectBedrock",
    "connectOllama",
    "connectOpenAI",
    "connectSelfHostedLLM",
    "tool",
]

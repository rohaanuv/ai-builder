"""Factory functions that return a configured :class:`~ai_builder.tools.llm.tool.LLMTool`."""

from ai_builder.tools.llm.connectors.anthropic import connectAnthropic, connect_anthropic
from ai_builder.tools.llm.connectors.azure import connectAzure, connect_azure
from ai_builder.tools.llm.connectors.bedrock import connectBedrock, connect_bedrock
from ai_builder.tools.llm.connectors.ollama import connectOllama, connect_ollama
from ai_builder.tools.llm.connectors.openai import connectOpenAI, connect_openai
from ai_builder.tools.llm.connectors.self_hosted import (
    connectSelfHostedLLM,
    connect_self_hosted_llm,
)

__all__ = [
    "connect_anthropic",
    "connectAnthropic",
    "connect_azure",
    "connectAzure",
    "connect_bedrock",
    "connectBedrock",
    "connect_ollama",
    "connectOllama",
    "connect_openai",
    "connectOpenAI",
    "connect_self_hosted_llm",
    "connectSelfHostedLLM",
]

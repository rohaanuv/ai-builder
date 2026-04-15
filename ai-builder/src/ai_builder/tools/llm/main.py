"""LLMTool — generate text from a prompt using OpenAI, Anthropic, or Ollama."""

from __future__ import annotations

import logging
import os
from typing import Any

from pydantic import Field

from ai_builder.core.tool import BaseTool, ToolInput, ToolOutput
from ai_builder.tools.llm.config import LLMConfig

logger = logging.getLogger(__name__)


class LLMInput(ToolInput):
    """Input: prompt text in .data, optional context in .metadata['context']."""

    data: str = Field(default="", description="User prompt")


class LLMOutput(ToolOutput):
    """Output: generated text in .data."""

    data: str = Field(default="", description="Generated response")


class LLMTool(BaseTool[LLMInput, LLMOutput]):
    """
    Generate text using OpenAI, Anthropic, or Ollama. Commonly used as the
    final step in a RAG pipeline (retriever output -> LLM input).
    """

    name = "llm"
    description = "Generate text using LLM (OpenAI, Anthropic, Ollama)"
    version = "1.0.0"

    def __init__(self, config: LLMConfig | None = None) -> None:
        self.config = config or LLMConfig()

    def execute(self, inp: LLMInput) -> LLMOutput:
        prompt = inp.data if isinstance(inp.data, str) else str(inp.data)
        context = inp.metadata.get("context", "")

        if context:
            full_prompt = f"Context:\n{context}\n\nQuestion: {prompt}"
        else:
            full_prompt = prompt

        provider = self.config.provider
        try:
            if provider == "openai":
                response = self._call_openai(full_prompt)
            elif provider == "anthropic":
                response = self._call_anthropic(full_prompt)
            elif provider == "ollama":
                response = self._call_ollama(full_prompt)
            else:
                return LLMOutput(data="", success=False, error=f"Unknown provider: {provider}")
        except Exception as exc:
            return LLMOutput(data="", success=False, error=str(exc))

        return LLMOutput(
            data=response,
            metadata={**inp.metadata, "model": self.config.model, "provider": provider},
        )

    def _call_openai(self, prompt: str) -> str:
        from openai import OpenAI

        key = self.config.api_key or os.getenv("OPENAI_API_KEY", "")
        kwargs: dict[str, Any] = {"api_key": key}
        if self.config.base_url:
            kwargs["base_url"] = self.config.base_url

        client = OpenAI(**kwargs)
        resp = client.chat.completions.create(
            model=self.config.model,
            messages=[
                {"role": "system", "content": self.config.system_prompt},
                {"role": "user", "content": prompt},
            ],
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
        )
        return resp.choices[0].message.content or ""

    def _call_anthropic(self, prompt: str) -> str:
        from anthropic import Anthropic

        key = self.config.api_key or os.getenv("ANTHROPIC_API_KEY", "")
        client = Anthropic(api_key=key)
        resp = client.messages.create(
            model=self.config.model,
            system=self.config.system_prompt,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
        )
        return resp.content[0].text

    def _call_ollama(self, prompt: str) -> str:
        from openai import OpenAI

        base = self.config.base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        client = OpenAI(api_key="ollama", base_url=f"{base}/v1")
        resp = client.chat.completions.create(
            model=self.config.model,
            messages=[
                {"role": "system", "content": self.config.system_prompt},
                {"role": "user", "content": prompt},
            ],
            temperature=self.config.temperature,
        )
        return resp.choices[0].message.content or ""


tool = LLMTool()

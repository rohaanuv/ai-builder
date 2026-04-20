"""LLMTool — generate text via OpenAI, Anthropic, Ollama, self-hosted, Bedrock, or Azure."""

from __future__ import annotations

import base64
import json
import logging
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from ai_builder.core.tool import BaseTool

from ai_builder.tools.llm.config import LLMConfig
from ai_builder.tools.llm.types import LLMInput, LLMOutput

logger = logging.getLogger(__name__)


class LLMTool(BaseTool[LLMInput, LLMOutput]):
    """
    Generate text using a configured provider.

    Prefer provider factories in ``connectors`` (e.g. ``connect_openai()``) for clearer setup.
    """

    name = "llm"
    description = "Generate text using LLM (OpenAI, Anthropic, Ollama, Bedrock, Azure, …)"
    version = "2.0.0"

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
            elif provider == "self_hosted":
                response = self._call_self_hosted(full_prompt)
            elif provider == "bedrock":
                response = self._call_bedrock(full_prompt)
            elif provider == "azure":
                response = self._call_azure(full_prompt)
            else:
                return LLMOutput(data="", success=False, error=f"Unknown provider: {provider}")
        except Exception as exc:
            logger.exception("LLM call failed")
            return LLMOutput(data="", success=False, error=str(exc))

        return LLMOutput(
            data=response,
            metadata={
                **inp.metadata,
                "model": self.config.model,
                "provider": provider,
            },
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
        client = OpenAI(api_key="ollama", base_url=f"{base.rstrip('/')}/v1")
        resp = client.chat.completions.create(
            model=self.config.model,
            messages=[
                {"role": "system", "content": self.config.system_prompt},
                {"role": "user", "content": prompt},
            ],
            temperature=self.config.temperature,
        )
        return resp.choices[0].message.content or ""

    def _call_self_hosted(self, prompt: str) -> str:
        """OpenAI-compatible HTTP API (vLLM, LiteLLM proxy, etc.)."""
        from openai import OpenAI

        base = self.config.base_url or os.getenv("SELF_HOSTED_BASE_URL", "")
        if not base:
            raise ValueError("self_hosted provider requires base_url (or SELF_HOSTED_BASE_URL)")

        key = self.config.api_key or os.getenv("SELF_HOSTED_API_KEY", "EMPTY")
        headers: dict[str, str] = {}

        token = self.config.auth_token or os.getenv("SELF_HOSTED_TOKEN", "")
        if token:
            headers["Authorization"] = f"Bearer {token}"

        user = self.config.username or os.getenv("SELF_HOSTED_USERNAME", "")
        pwd = self.config.password or os.getenv("SELF_HOSTED_PASSWORD", "")
        if user and pwd:
            raw = base64.b64encode(f"{user}:{pwd}".encode()).decode()
            headers["Authorization"] = f"Basic {raw}"

        kwargs: dict[str, Any] = {"api_key": key, "base_url": base.rstrip("/")}
        if headers:
            kwargs["default_headers"] = headers

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

    def _call_bedrock(self, prompt: str) -> str:
        from anthropic import AnthropicBedrock

        region = self.config.aws_region or os.getenv("AWS_REGION", "us-east-1")
        kwargs: dict[str, Any] = {"aws_region": region}

        ak = self.config.aws_access_key_id or os.getenv("AWS_ACCESS_KEY_ID", "")
        sk = self.config.aws_secret_access_key or os.getenv("AWS_SECRET_ACCESS_KEY", "")
        st = self.config.aws_session_token or os.getenv("AWS_SESSION_TOKEN", "")
        if ak and sk:
            kwargs["aws_access_key"] = ak
            kwargs["aws_secret_key"] = sk
        if st:
            kwargs["aws_session_token"] = st

        bearer = (
            self.config.aws_bearer_token
            or os.getenv("AWS_BEARER_TOKEN_BEDROCK", "")
        )
        if bearer:
            kwargs["default_headers"] = {"Authorization": f"Bearer {bearer}"}

        client = AnthropicBedrock(**kwargs)
        model = self.config.model or os.getenv("ANTHROPIC_MODEL", "")
        if not model:
            raise ValueError("Bedrock requires model (or ANTHROPIC_MODEL in the environment)")

        max_tokens = int(
            os.getenv(
                "CLAUDE_CODE_MAX_OUTPUT_TOKENS",
                str(self.config.max_tokens),
            ),
        )

        resp = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=self.config.system_prompt,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.config.temperature,
        )
        return resp.content[0].text

    def _azure_fetch_oauth_token(self) -> str:
        token_url = self.config.azure_token_url or os.getenv("AZURE_TOKEN_URL", "")
        cid = self.config.azure_client_id or os.getenv("AZURE_CLIENT_ID", "")
        secret = self.config.azure_client_secret or os.getenv("AZURE_CLIENT_SECRET", "")
        scope = self.config.azure_scope or os.getenv("AZURE_TOKEN_SCOPE", "")
        if not all([token_url, cid, secret, scope]):
            raise ValueError(
                "Azure OAuth requires azure_token_url, azure_client_id, azure_client_secret, "
                "azure_scope (or AZURE_TOKEN_URL, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TOKEN_SCOPE)",
            )

        body = urllib.parse.urlencode(
            {
                "grant_type": "client_credentials",
                "client_id": cid,
                "client_secret": secret,
                "scope": scope,
            },
        ).encode()

        req = urllib.request.Request(
            token_url,
            data=body,
            method="POST",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                payload = json.loads(resp.read())
        except urllib.error.HTTPError as exc:
            raise RuntimeError(f"Azure token request failed: {exc.read().decode(errors='replace')}") from exc

        token = payload.get("access_token")
        if not token:
            raise RuntimeError("Azure token response missing access_token")
        return str(token)

    def _call_azure(self, prompt: str) -> str:
        """Azure OpenAI–style chat completions (OAuth Bearer or API key)."""
        endpoint = self.config.azure_endpoint or os.getenv("AZURE_OPENAI_ENDPOINT", "")
        deployment = self.config.azure_deployment or os.getenv("AZURE_OPENAI_DEPLOYMENT", "")
        version = self.config.azure_api_version or os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")

        if not endpoint or not deployment:
            raise ValueError(
                "Azure requires azure_endpoint and azure_deployment "
                "(or AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_DEPLOYMENT)",
            )

        use_oauth = self.config.azure_use_oauth or bool(os.getenv("AZURE_CLIENT_ID"))
        if use_oauth:
            access = self._azure_fetch_oauth_token()
            auth_headers = {
                "Authorization": f"Bearer {access}",
                "Content-Type": "application/json",
            }
        else:
            api_key = self.config.api_key or os.getenv("AZURE_OPENAI_API_KEY", "")
            if not api_key:
                raise ValueError("Azure API key mode requires api_key or AZURE_OPENAI_API_KEY")
            auth_headers = {"api-key": api_key, "Content-Type": "application/json"}

        temperature = float(os.getenv("AZURE_OPENAI_TEMPERATURE", str(self.config.temperature)))
        max_tok = int(os.getenv("AZURE_OPENAI_MAX_TOKENS", str(self.config.max_tokens)))

        base = endpoint.rstrip("/")
        if "/deployments/" in base:
            url = f"{base}/chat/completions?api-version={urllib.parse.quote(version)}"
        else:
            url = (
                f"{base}/deployments/{urllib.parse.quote(deployment)}"
                f"/chat/completions?api-version={urllib.parse.quote(version)}"
            )

        body = json.dumps(
            {
                "messages": [
                    {"role": "system", "content": self.config.system_prompt},
                    {"role": "user", "content": prompt},
                ],
                "temperature": temperature,
                "max_tokens": max_tok,
            },
        ).encode()

        req = urllib.request.Request(url, data=body, method="POST", headers=auth_headers)
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                payload = json.loads(resp.read())
        except urllib.error.HTTPError as exc:
            raise RuntimeError(exc.read().decode(errors="replace")) from exc

        choices = payload.get("choices") or []
        if not choices:
            raise RuntimeError(f"Unexpected Azure response: {payload}")
        msg = choices[0].get("message") or {}
        return str(msg.get("content") or "")


tool = LLMTool()

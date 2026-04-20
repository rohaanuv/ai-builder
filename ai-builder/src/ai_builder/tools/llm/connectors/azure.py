"""Azure OpenAI chat completions (OAuth2 client-credentials or classic API key)."""

from __future__ import annotations

from ai_builder.tools.llm.config import LLMConfig
from ai_builder.tools.llm.tool import LLMTool


def connect_azure(
    *,
    endpoint: str = "",
    deployment: str = "",
    model: str = "",
    api_key: str = "",
    api_version: str = "2024-02-01",
    use_oauth: bool = False,
    token_url: str = "",
    client_id: str = "",
    client_secret: str = "",
    scope: str = "",
    temperature: float = 0.7,
    max_tokens: int = 10000,
    system_prompt: str = "You are a helpful assistant.",
) -> LLMTool:
    """
    OAuth mode (``use_oauth=True`` or set ``AZURE_CLIENT_ID`` in the environment):
    uses token URL + client credentials, then calls the deployment with Bearer auth.

    API key mode: set ``api_key`` or ``AZURE_OPENAI_API_KEY`` and ``use_oauth=False``.
    """
    return LLMTool(
        LLMConfig(
            provider="azure",
            model=model or deployment,
            api_key=api_key,
            temperature=temperature,
            max_tokens=max_tokens,
            system_prompt=system_prompt,
            azure_endpoint=endpoint,
            azure_deployment=deployment,
            azure_api_version=api_version,
            azure_use_oauth=use_oauth,
            azure_token_url=token_url,
            azure_client_id=client_id,
            azure_client_secret=client_secret,
            azure_scope=scope,
        ),
    )


connectAzure = connect_azure

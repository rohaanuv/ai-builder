"""Configuration for LLM connectors (OpenAI-compatible and managed APIs)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

Provider = Literal[
    "openai",
    "anthropic",
    "ollama",
    "self_hosted",
    "bedrock",
    "azure",
]


class LLMConfig(BaseModel):
    """Provider-specific settings; secrets usually come from env or connector kwargs."""

    provider: Provider = Field(default="openai", description="LLM backend")
    model: str = Field(default="gpt-4o-mini", description="Model id or deployment name")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=4096, ge=1)
    system_prompt: str = Field(default="You are a helpful assistant.")

    api_key: str = Field(default="", description="API key or placeholder (see provider)")
    base_url: str = Field(default="", description="Custom base URL (Ollama, vLLM, OpenAI-compatible)")

    # Self-hosted / OpenAI-compatible auth
    auth_token: str = Field(default="", description="Bearer token (alternative to api_key)")
    username: str = Field(default="", description="HTTP Basic username")
    password: str = Field(default="", description="HTTP Basic password")

    # AWS Bedrock (Anthropic Claude on Bedrock)
    aws_region: str = Field(default="", description="AWS region for Bedrock")
    aws_access_key_id: str = Field(default="", description="AWS access key (optional if env/profile)")
    aws_secret_access_key: str = Field(default="", description="AWS secret key")
    aws_session_token: str = Field(default="", description="AWS session token (STS)")
    aws_bearer_token: str = Field(default="", description="Bearer token for Bedrock HTTP auth if used")

    # Azure OpenAI (API key mode or OAuth2 client credentials)
    azure_endpoint: str = Field(default="", description="Azure OpenAI resource URL (with path if required)")
    azure_deployment: str = Field(default="", description="Deployment name")
    azure_api_version: str = Field(default="2024-02-01")
    azure_use_oauth: bool = Field(
        default=False,
        description="Use OAuth2 client-credentials (token URL + client id/secret)",
    )
    azure_token_url: str = Field(default="")
    azure_client_id: str = Field(default="")
    azure_client_secret: str = Field(default="")
    azure_scope: str = Field(default="")

    model_config = {"extra": "allow"}

"""Base configuration using pydantic-settings — auto-loads from .env files."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic_settings import BaseSettings


class BaseConfig(BaseSettings):
    """
    Base config for any ai-builder project.

    Automatically reads from .env in the project root.
    Subclass and add your own fields:

        class MyConfig(BaseConfig):
            openai_api_key: str = ""
            model_name: str = "gpt-4o-mini"
    """

    project_name: str = "ai-builder-project"
    log_level: str = "INFO"
    data_dir: Path = Path("data")

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}

    def to_dict(self) -> dict[str, Any]:
        return {k: str(v) if isinstance(v, Path) else v for k, v in self.model_dump().items()}

"""Per–sentence-transformers model: uv extra names and pip packages for scaffolds."""

from __future__ import annotations

from .config import SUPPORTED_MODELS


def _slug(model_id: str) -> str:
    s = (
        model_id.replace("sentence-transformers/", "st-")
        .replace("BAAI/", "baai-")
        .replace("thenlper/", "thenlper-")
        .replace("/", "-")
        .replace(".", "-")
        .lower()
    )
    return s.replace("--", "-")


def extra_name_for_model(model_id: str) -> str:
    """pyproject optional-extra key, e.g. embed-model-baai-bge-m3."""
    return f"embed-model-{_slug(model_id)}"


def packages_for_model(model_id: str) -> tuple[str, ...]:
    """
    Pip requirement lines for this HF model.

    Most models only need sentence-transformers; BGE-M3 benefits from sentencepiece.
    """
    base = ("sentence-transformers>=3.3",)
    if "bge-m3" in model_id.lower():
        return (*base, "sentencepiece>=0.1.99")
    return base


EMBEDDING_EXTRA_BY_MODEL: dict[str, str] = {
    mid: extra_name_for_model(mid) for mid in SUPPORTED_MODELS
}

EMBEDDING_PACKAGES_BY_MODEL: dict[str, tuple[str, ...]] = {
    mid: packages_for_model(mid) for mid in SUPPORTED_MODELS
}

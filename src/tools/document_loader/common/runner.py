"""Shared filesystem walk + extract loop for document loaders."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from .extract import extract_for_path
from .schemas import LoaderConfig, LoaderInput, LoaderOutput

logger = logging.getLogger(__name__)


def run_loader(
    inp: LoaderInput,
    config: LoaderConfig,
    allowed_suffixes: set[str],
) -> LoaderOutput:
    source = Path(inp.data) if inp.data else Path(config.source_dir)
    if not source.exists():
        return LoaderOutput(data=[], success=False, error=f"Path not found: {source}")

    files = _collect_files(source, config, allowed_suffixes)
    docs: list[dict[str, Any]] = []
    errors: list[str] = []

    for f in files:
        try:
            text = extract_for_path(f, allowed_suffixes=allowed_suffixes)
            if text:
                docs.append({
                    "text": text,
                    "source": str(f),
                    "filename": f.name,
                    "format": f.suffix.lower().lstrip("."),
                    "chars": len(text),
                })
        except NotImplementedError as exc:
            errors.append(f"{f.name}: {exc}")
            logger.warning("%s", exc)
        except Exception as exc:
            errors.append(f"{f.name}: {exc}")
            logger.warning("Failed to extract %s: %s", f, exc)

    return LoaderOutput(
        data=docs,
        metadata={
            **inp.metadata,
            "file_count": len(docs),
            "error_count": len(errors),
            "source_dir": str(source),
            "errors": errors,
        },
    )


def _collect_files(source: Path, config: LoaderConfig, allowed: set[str]) -> list[Path]:
    suffixes = set(config.supported_formats) & allowed if config.supported_formats else allowed
    if source.is_file():
        return [source] if source.suffix.lower() in suffixes else []
    glob_fn = source.rglob if config.recursive else source.glob
    return sorted(f for f in glob_fn("*") if f.is_file() and f.suffix.lower() in suffixes)

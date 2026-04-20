"""Local filesystem / EFS mount — absolute path required."""

from __future__ import annotations

import os
from pathlib import Path

from ai_builder.core.tool import BaseTool, ToolInput, ToolOutput


class LocalFilesystemDataSource(BaseTool):
    """
    Resolve ``DATA_SOURCE_LOCAL_PATH`` to an absolute directory.

    AWS EFS is supported the same way: mount the file system and set the path to the mount.
    """

    name = "data_source_local"
    description = "Use a local or EFS-mounted absolute path as the document root"
    version = "1.0.0"

    def execute(self, inp: ToolInput) -> ToolOutput:
        raw = (
            (inp.data if isinstance(inp.data, str) else None)
            or inp.metadata.get("path")
            or os.getenv("DATA_SOURCE_LOCAL_PATH", "")
        ).strip()
        if not raw:
            return ToolOutput(
                data="",
                success=False,
                error="Set DATA_SOURCE_LOCAL_PATH to an absolute directory path",
            )
        path = Path(raw).expanduser().resolve()
        if not path.is_absolute():
            return ToolOutput(
                data="",
                success=False,
                error=f"Path must be absolute: {path}",
            )
        if not path.exists():
            return ToolOutput(data="", success=False, error=f"Path not found: {path}")
        if not path.is_dir():
            return ToolOutput(data="", success=False, error=f"Not a directory: {path}")
        return ToolOutput(data=str(path), metadata={"kind": "local"})


tool = LocalFilesystemDataSource()

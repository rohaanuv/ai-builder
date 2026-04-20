"""Google Drive — placeholder until OAuth flows are wired in your app."""

from __future__ import annotations

from ai_builder.core.tool import BaseTool, ToolInput, ToolOutput


class GoogleDriveDataSource(BaseTool):
    name = "data_source_gdrive"
    description = "Google Drive corpus (implement OAuth + Drive API export in your deployment)"
    version = "1.0.0"

    def execute(self, inp: ToolInput) -> ToolOutput:
        return ToolOutput(
            data="",
            success=False,
            error=(
                "Google Drive ingestion is not implemented in-process. "
                'Install extras (data-gdrive), then export files to a local path or '
                "implement Drive API sync using google-api-python-client."
            ),
        )

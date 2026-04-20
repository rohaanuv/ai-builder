"""Microsoft OneDrive — placeholder (use MS Graph + MSAL in your app)."""

from __future__ import annotations

from ai_builder.core.tool import BaseTool, ToolInput, ToolOutput


class OneDriveDataSource(BaseTool):
    name = "data_source_onedrive"
    description = "OneDrive corpus (implement MSAL + Graph download in your deployment)"
    version = "1.0.0"

    def execute(self, inp: ToolInput) -> ToolOutput:
        return ToolOutput(
            data="",
            success=False,
            error=(
                "OneDrive ingestion is not implemented in-process. "
                'Install extras (data-onedrive), then sync to a local directory or '
                "implement Microsoft Graph file download with msal."
            ),
        )

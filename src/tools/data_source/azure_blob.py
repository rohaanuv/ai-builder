"""Azure Blob Storage — sync a prefix to a temp directory."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

from ai_builder.core.tool import BaseTool, ToolInput, ToolOutput


class AzureBlobDataSource(BaseTool):
    name = "data_source_azure_blob"
    description = "Sync a blob prefix to a temp directory (DefaultAzureCredential or connection string)"
    version = "1.0.0"

    def execute(self, inp: ToolInput) -> ToolOutput:
        try:
            from azure.storage.blob import BlobServiceClient
        except ModuleNotFoundError:
            return ToolOutput(
                data="",
                success=False,
                error='Install azure packages: pip install "ai-builder[data-azure-blob]" or data-azure-blob extra',
            )

        account = os.getenv("AZURE_STORAGE_ACCOUNT_NAME", "").strip()
        container = os.getenv("AZURE_STORAGE_CONTAINER", "").strip()
        prefix = os.getenv("AZURE_STORAGE_PREFIX", "").strip()
        conn = os.getenv("AZURE_STORAGE_CONNECTION_STRING", "").strip()

        if not container:
            return ToolOutput(data="", success=False, error="Set AZURE_STORAGE_CONTAINER")

        if conn:
            service = BlobServiceClient.from_connection_string(conn)
        else:
            if not account:
                return ToolOutput(
                    data="",
                    success=False,
                    error="Set AZURE_STORAGE_CONNECTION_STRING or AZURE_STORAGE_ACCOUNT_NAME",
                )
            try:
                from azure.identity import DefaultAzureCredential
            except ModuleNotFoundError:
                return ToolOutput(
                    data="",
                    success=False,
                    error="Install azure-identity for account-name auth",
                )
            url = f"https://{account}.blob.core.windows.net"
            service = BlobServiceClient(url, credential=DefaultAzureCredential())

        tmp = tempfile.mkdtemp(prefix="rag-azure-")
        cc = service.get_container_client(container)
        n = 0
        for blob in cc.list_blobs(name_starts_with=prefix if prefix else None):
            if blob.name.endswith("/"):
                continue
            rel = blob.name[len(prefix) :].lstrip("/") if prefix else blob.name
            dest = Path(tmp) / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            bc = cc.get_blob_client(blob.name)
            with open(dest, "wb") as f:
                stream = bc.download_blob()
                f.write(stream.readall())
            n += 1

        return ToolOutput(data=tmp, metadata={"kind": "azure_blob_sync", "files": n})

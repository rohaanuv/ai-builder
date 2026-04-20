"""Google Cloud Storage — sync a prefix to a temp directory."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

from ai_builder.core.tool import BaseTool, ToolInput, ToolOutput


class GcsDataSource(BaseTool):
    name = "data_source_gcs"
    description = "Sync a GCS prefix into a temp directory (GOOGLE_APPLICATION_CREDENTIALS)"
    version = "1.0.0"

    def execute(self, inp: ToolInput) -> ToolOutput:
        try:
            from google.cloud import storage
        except ModuleNotFoundError:
            return ToolOutput(
                data="",
                success=False,
                error='Install google-cloud-storage (e.g. project extra data-gcs)',
            )

        bucket_name = os.getenv("DATA_SOURCE_GCS_BUCKET", "").strip()
        prefix = os.getenv("DATA_SOURCE_GCS_PREFIX", "").strip()

        if not bucket_name:
            return ToolOutput(data="", success=False, error="Set DATA_SOURCE_GCS_BUCKET")

        client = storage.Client()
        bucket = client.bucket(bucket_name)
        tmp = tempfile.mkdtemp(prefix="rag-gcs-")
        n = 0
        for blob in bucket.list_blobs(prefix=prefix if prefix else None):
            name = blob.name
            if name.endswith("/"):
                continue
            rel = name[len(prefix) :].lstrip("/") if prefix else name
            dest = Path(tmp) / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            blob.download_to_filename(str(dest))
            n += 1

        return ToolOutput(data=tmp, metadata={"kind": "gcs_sync", "files": n})

"""AWS S3 and S3-compatible endpoints (MinIO, Ceph RADOS Gateway)."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

from ai_builder.core.tool import BaseTool, ToolInput, ToolOutput


class S3CompatibleDataSource(BaseTool):
    """Download ``DATA_SOURCE_S3_PREFIX`` under a bucket into a temporary directory."""

    version = "1.0.0"

    def __init__(self, *, tool_name: str, description: str) -> None:
        super().__init__()
        self.name = tool_name
        self.description = description

    def execute(self, inp: ToolInput) -> ToolOutput:
        try:
            import boto3
        except ModuleNotFoundError:
            return ToolOutput(
                data="",
                success=False,
                error='Install boto3 (e.g. pip install "ai-builder[data-s3]" or project extra data-s3)',
            )

        bucket = os.getenv("DATA_SOURCE_S3_BUCKET", "").strip()
        prefix = os.getenv("DATA_SOURCE_S3_PREFIX", "").strip()
        endpoint = os.getenv("DATA_SOURCE_S3_ENDPOINT_URL", "").strip() or None
        region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")

        if not bucket:
            return ToolOutput(data="", success=False, error="Set DATA_SOURCE_S3_BUCKET")

        client = boto3.client("s3", endpoint_url=endpoint, region_name=region)
        tmp = tempfile.mkdtemp(prefix="rag-s3-")

        paginator = client.get_paginator("list_objects_v2")
        n = 0
        for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
            for obj in page.get("Contents", []):
                key = obj["Key"]
                if key.endswith("/"):
                    continue
                rel = key[len(prefix) :].lstrip("/") if prefix else key
                dest = Path(tmp) / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                client.download_file(bucket, key, str(dest))
                n += 1

        return ToolOutput(
            data=tmp,
            metadata={"kind": "s3_sync", "files": n, "endpoint": endpoint or "aws"},
        )


class S3DataSource(S3CompatibleDataSource):
    def __init__(self) -> None:
        super().__init__(
            tool_name="data_source_s3",
            description="Sync documents from AWS S3 into a temp directory",
        )


class MinioDataSource(S3CompatibleDataSource):
    def __init__(self) -> None:
        super().__init__(
            tool_name="data_source_minio",
            description="Sync from MinIO (set DATA_SOURCE_S3_ENDPOINT_URL)",
        )


class CephRgwDataSource(S3CompatibleDataSource):
    def __init__(self) -> None:
        super().__init__(
            tool_name="data_source_ceph_s3",
            description="Sync from Ceph RGW S3 API (set DATA_SOURCE_S3_ENDPOINT_URL)",
        )

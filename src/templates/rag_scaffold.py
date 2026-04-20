"""RAG template: pyproject.toml / requirements.txt / .env from scaffold choices."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from ai_builder.tools.embeddings.config import SUPPORTED_MODELS
from ai_builder.tools.embeddings.registry import (
    EMBEDDING_EXTRA_BY_MODEL,
    EMBEDDING_PACKAGES_BY_MODEL,
)

# Default ST model (first entry in SUPPORTED_MODELS must match EmbedderConfig).
DEFAULT_EMBEDDING_MODEL_ID: str = next(iter(SUPPORTED_MODELS))

# Keys used in RagScaffoldChoices.formats (subset selected in wizard).
FORMAT_GROUPS: dict[str, tuple[str, ...]] = {
    "pdf": ("pdfplumber>=0.11",),
    "word": ("python-docx>=1.1", "docx2txt>=0.8"),
    "slides": ("python-pptx>=1.0",),
    "html": ("beautifulsoup4>=4.12",),
    "rtf": ("striprtf>=0.0.26",),
    "spreadsheet": ("openpyxl>=3.1", "xlrd>=2.0"),
    "epub": ("ebooklib>=0.18", "beautifulsoup4>=4.12"),
    "odt": ("odfpy>=1.4",),
}

EmbeddingChoice = Literal["none", "local", "openai_api"]

# Built-in VectorStoreWriter today: faiss, chroma, qdrant. Others: install client; wire in your app.
VectorBackendChoice = Literal[
    "none",
    "faiss",
    "qdrant",
    "chroma",
    "opensearch",
    "milvus",
    "mongodb",
    "postgres",
    "weaviate",
    "vald",
    "redis",
    "lancedb",
]

DataSourceChoice = Literal[
    "local",
    "efs",
    "s3",
    "azure_blob",
    "gcs",
    "gdrive",
    "onedrive",
    "minio",
    "ceph_s3",
]

LlmChoice = Literal["none", "openai", "anthropic", "bedrock", "azure", "ollama", "self_hosted"]

# pip lines per vector backend (extras names in pyproject use vector-* except faiss/qdrant/chroma).
VECTOR_BACKEND_PACKAGES: dict[str, tuple[str, ...]] = {
    "none": (),
    "faiss": ("faiss-cpu>=1.9",),
    "qdrant": ("qdrant-client>=1.12",),
    "chroma": ("chromadb>=0.5",),
    "opensearch": ("opensearch-py>=2.4",),
    "milvus": ("pymilvus>=2.4",),
    "mongodb": ("pymongo>=4.6",),
    "postgres": ("psycopg[binary]>=3.1", "pgvector>=0.2"),
    "weaviate": ("weaviate-client>=4.4",),
    "vald": ("grpcio>=1.60", "protobuf>=4.21"),
    "redis": ("redis>=5.0",),
    "lancedb": ("lancedb>=0.6",),
}

# uv/pyproject optional extra key per backend (must exist in _optional_deps_block).
VECTOR_BACKEND_EXTRA: dict[str, str] = {
    "none": "",
    "faiss": "faiss",
    "qdrant": "qdrant",
    "chroma": "chroma",
    "opensearch": "vector-opensearch",
    "milvus": "vector-milvus",
    "mongodb": "vector-mongodb",
    "postgres": "vector-postgres",
    "weaviate": "vector-weaviate",
    "vald": "vector-vald",
    "redis": "vector-redis",
    "lancedb": "vector-lancedb",
}

DATA_SOURCE_PACKAGES: dict[str, tuple[str, ...]] = {
    "local": (),
    "efs": (),
    "s3": ("boto3>=1.34",),
    "azure_blob": ("azure-storage-blob>=12.19", "azure-identity>=1.14"),
    "gcs": ("google-cloud-storage>=2.14",),
    "gdrive": ("google-api-python-client>=2.100", "google-auth-oauthlib>=1.2"),
    "onedrive": ("msal>=1.26", "requests>=2.31"),
    "minio": ("boto3>=1.34",),
    "ceph_s3": ("boto3>=1.34",),
}

DATA_SOURCE_EXTRA: dict[str, str] = {
    "local": "",
    "efs": "",
    "s3": "data-s3",
    "azure_blob": "data-azure-blob",
    "gcs": "data-gcs",
    "gdrive": "data-gdrive",
    "onedrive": "data-onedrive",
    "minio": "data-minio",
    "ceph_s3": "data-ceph-s3",
}


@dataclass
class RagScaffoldChoices:
    """Selections from `ai-builder create rag` wizard (or defaults)."""

    data_source: DataSourceChoice = "local"
    embedding: EmbeddingChoice = "local"
    embedding_model_id: str = field(default_factory=lambda: DEFAULT_EMBEDDING_MODEL_ID)
    vector_backend: VectorBackendChoice = "faiss"
    llm: LlmChoice = "none"
    formats: frozenset[str] = field(default_factory=lambda: frozenset(FORMAT_GROUPS))

    @classmethod
    def wizard_default(cls) -> RagScaffoldChoices:
        return cls()

    @classmethod
    def non_interactive_default(cls) -> RagScaffoldChoices:
        return cls(
            data_source="local",
            embedding="local",
            embedding_model_id=DEFAULT_EMBEDDING_MODEL_ID,
            vector_backend="faiss",
            llm="none",
            formats=frozenset(FORMAT_GROUPS),
        )


def _embed_model_optional_deps_lines() -> str:
    """One pyproject optional-extra per sentence-transformers model (minimal pip set)."""
    lines: list[str] = []
    for mid in sorted(EMBEDDING_EXTRA_BY_MODEL.keys(), key=lambda m: EMBEDDING_EXTRA_BY_MODEL[m]):
        extra = EMBEDDING_EXTRA_BY_MODEL[mid]
        pkgs = EMBEDDING_PACKAGES_BY_MODEL[mid]
        inner = ", ".join(f'"{p}"' for p in pkgs)
        lines.append(f"{extra} = [{inner}]")
    return "\n".join(lines)


def _optional_deps_block(project_name: str) -> str:
    """Full optional-dependencies table."""
    embed_per_model = _embed_model_optional_deps_lines()
    return f'''[project.optional-dependencies]
notebook = ["ipykernel>=6.29"]
embeddings-local = ["sentence-transformers>=3.3"]
embeddings-openai = ["openai>=1.0"]
embeddings = ["sentence-transformers>=3.3"]
{embed_per_model}
faiss = ["faiss-cpu>=1.9"]
pdf = ["pdfplumber>=0.11"]
word = ["python-docx>=1.1", "docx2txt>=0.8"]
slides = ["python-pptx>=1.0"]
html = ["beautifulsoup4>=4.12"]
rtf = ["striprtf>=0.0.26"]
spreadsheet = ["openpyxl>=3.1", "xlrd>=2.0"]
epub = ["ebooklib>=0.18", "beautifulsoup4>=4.12"]
odt = ["odfpy>=1.4"]
docs = [
    "pdfplumber>=0.11",
    "python-docx>=1.1",
    "python-pptx>=1.0",
    "beautifulsoup4>=4.12",
    "striprtf>=0.0.26",
    "openpyxl>=3.1",
    "docx2txt>=0.8",
    "xlrd>=2.0",
    "ebooklib>=0.18",
    "odfpy>=1.4",
]
llm-openai = ["openai>=1.0"]
llm-anthropic = ["anthropic>=0.40"]
llm-bedrock = ["anthropic>=0.40"]
llm = ["openai>=1.0", "anthropic>=0.40"]
chroma = ["chromadb>=0.5"]
qdrant = ["qdrant-client>=1.12"]
vector-opensearch = ["opensearch-py>=2.4"]
vector-milvus = ["pymilvus>=2.4"]
vector-mongodb = ["pymongo>=4.6"]
vector-postgres = ["psycopg[binary]>=3.1", "pgvector>=0.2"]
vector-weaviate = ["weaviate-client>=4.4"]
vector-vald = ["grpcio>=1.60", "protobuf>=4.21"]
vector-redis = ["redis>=5.0"]
vector-lancedb = ["lancedb>=0.6"]
data-s3 = ["boto3>=1.34"]
data-minio = ["boto3>=1.34"]
data-ceph-s3 = ["boto3>=1.34"]
data-azure-blob = ["azure-storage-blob>=12.19", "azure-identity>=1.14"]
data-gcs = ["google-cloud-storage>=2.14"]
data-gdrive = ["google-api-python-client>=2.100", "google-auth-oauthlib>=1.2"]
data-onedrive = ["msal>=1.26", "requests>=2.31"]
dev = ["pytest>=8.0"]
all = ["{project_name}[notebook,embeddings-local,faiss,docs,llm,qdrant]"]
'''


def render_pyproject_toml(project_name: str, choices: RagScaffoldChoices | None) -> str:
    _ = choices
    body = f'''[project]
name = "{project_name}"
version = "0.1.0"
description = "RAG pipeline: {project_name}"
requires-python = ">=3.13"
dependencies = [
    "ai-builder @ git+https://github.com/rohaanuv/ai-builder.git",
    "pydantic>=2.0",
    "langfuse>=2.0",
]

{_optional_deps_block(project_name)}
[tool.setuptools.packages.find]
where = ["src"]

[build-system]
requires = ["setuptools>=75"]
build-backend = "setuptools.build_meta"
'''
    return body


def _embedding_packages(kind: EmbeddingChoice, embedding_model_id: str) -> list[str]:
    if kind == "local":
        return list(EMBEDDING_PACKAGES_BY_MODEL.get(embedding_model_id, ("sentence-transformers>=3.3",)))
    if kind == "openai_api":
        return ["openai>=1.0"]
    return []


def _vector_backend_packages(kind: VectorBackendChoice) -> list[str]:
    return list(VECTOR_BACKEND_PACKAGES.get(kind, ()))


def _data_source_packages(kind: DataSourceChoice) -> list[str]:
    return list(DATA_SOURCE_PACKAGES.get(kind, ()))


def _llm_packages(kind: LlmChoice) -> list[str]:
    return {
        "none": [],
        "openai": ["openai>=1.0"],
        "anthropic": ["anthropic>=0.40"],
        "bedrock": ["anthropic>=0.40"],
        "azure": [],
        # Ollama / self-hosted use stdlib HTTP in LLMTool — no extra wheels
        "ollama": [],
        "self_hosted": [],
    }[kind]


def _dedupe_preserve(seq: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for x in seq:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


def selected_pip_packages(choices: RagScaffoldChoices) -> list[str]:
    pkgs: list[str] = []
    pkgs.extend(_data_source_packages(choices.data_source))
    pkgs.extend(_embedding_packages(choices.embedding, choices.embedding_model_id))
    pkgs.extend(_vector_backend_packages(choices.vector_backend))
    pkgs.extend(_llm_packages(choices.llm))
    for key in sorted(choices.formats):
        if key in FORMAT_GROUPS:
            pkgs.extend(FORMAT_GROUPS[key])
    return _dedupe_preserve(pkgs)


def selected_uv_extras(choices: RagScaffoldChoices) -> list[str]:
    xs: list[str] = []
    ds_ex = DATA_SOURCE_EXTRA.get(choices.data_source, "")
    if ds_ex:
        xs.append(ds_ex)
    if choices.embedding == "local":
        ex = EMBEDDING_EXTRA_BY_MODEL.get(choices.embedding_model_id, "")
        if ex:
            xs.append(ex)
        else:
            xs.append("embeddings-local")
    elif choices.embedding == "openai_api":
        xs.append("embeddings-openai")
    vs_ex = VECTOR_BACKEND_EXTRA.get(choices.vector_backend, "")
    if vs_ex:
        xs.append(vs_ex)
    if choices.llm == "openai":
        xs.append("llm-openai")
    elif choices.llm == "anthropic":
        xs.append("llm-anthropic")
    elif choices.llm == "bedrock":
        xs.append("llm-bedrock")
    elif choices.llm in ("ollama", "self_hosted"):
        pass  # optional extras not required — wire LLMConfig / env in your app
    for key in sorted(choices.formats):
        if key in FORMAT_GROUPS:
            xs.append(key)
    return xs


def render_requirements_txt(project_name: str, choices: RagScaffoldChoices | None) -> str:
    lines = [
        "# Core — also declared in pyproject.toml; keep in sync when editing by hand.",
        "ai-builder @ git+https://github.com/rohaanuv/ai-builder.git",
        "pydantic>=2.0",
        "langfuse>=2.0",
        "",
    ]
    if choices is None:
        lines.extend(
            [
                "# No interactive profile — pick optional stacks with uv, e.g.:",
                "#   uv pip install -e \".[embed-model-st-all-minilm-l6-v2,faiss,data-s3,vector-opensearch,pdf]\"",
                "# Document parsers: uv pip install -e \".[docs]\"",
                "",
            ],
        )
        return "\n".join(lines)

    sel = selected_pip_packages(choices)
    extras = ",".join(selected_uv_extras(choices))
    lines.extend(
        [
            f"# Profile for {project_name} (ai-builder create rag wizard).",
            f"# Same as: uv pip install -e \".[{extras}]\"",
            "",
        ],
    )
    lines.extend(sel)
    lines.append("")
    return "\n".join(lines)


def render_dot_env_example(project_name: str, choices: RagScaffoldChoices | None) -> str:
    """Example env vars for selected data source + vector backend."""
    c = choices or RagScaffoldChoices.non_interactive_default()

    lines = [
        '# Copy to ".env" and adjust (never commit real secrets).',
        "# cp .env.example .env",
        "",
        f"PROJECT_NAME={project_name}",
        "CHUNK_SIZE=1000",
        "CHUNK_OVERLAP=200",
        "LOG_LEVEL=INFO",
        "",
        "# --- Embeddings (sentence-transformers; Embedder + Retriever in full_rag) ---",
        f"EMBEDDING_MODEL_ID={c.embedding_model_id}",
        "",
        "# --- LLM (ai_builder.tools.llm — Provider in LLMConfig) ---",
        f"# Wizard choice: {c.llm}",
    ]

    llm_extra: dict[str, list[str]] = {
        "none": ["# LLMTool unused — install an llm-* extra later if needed."],
        "openai": [
            "OPENAI_API_KEY=",
            "# OPENAI_BASE_URL=https://api.openai.com/v1  # OpenAI-compatible proxies / Azure-style URLs",
        ],
        "anthropic": ["ANTHROPIC_API_KEY="],
        "bedrock": [
            "AWS_REGION=us-east-1",
            "# AWS_ACCESS_KEY_ID= … (or IAM role)",
            "# AWS_SECRET_ACCESS_KEY=",
            "# Claude on Bedrock via anthropic[boto] paths — see connectors/bedrock.py",
        ],
        "azure": [
            "AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/",
            "AZURE_OPENAI_API_KEY=",
            "# AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini",
        ],
        "ollama": [
            "# Ollama HTTP API — LLMTool uses urllib (no pip extra)",
            "OLLAMA_BASE_URL=http://localhost:11434",
            "# Model name defaults in code; set in LLMConfig(model=…)",
        ],
        "self_hosted": [
            "# vLLM, LiteLLM gateway, OpenAI-compatible — set base URL + model",
            "SELF_HOSTED_LLM_BASE_URL=http://localhost:8000/v1",
            "# SELF_HOSTED_LLM_API_KEY=  # optional bearer",
        ],
    }
    lines.extend(llm_extra.get(c.llm, []))
    lines.extend(
        [
            "",
            "# --- Data source (see ai_builder.tools.data_source) ---",
            f"DATA_SOURCE_TYPE={c.data_source}",
        ],
    )

    if c.data_source in ("local", "efs"):
        lines.extend(
            [
                "# Local or EFS: use an absolute path (EFS = mount path on this host).",
                "DATA_SOURCE_LOCAL_PATH=",
            ],
        )
    if c.data_source in ("s3", "minio", "ceph_s3"):
        lines.extend(
            [
                "AWS_ACCESS_KEY_ID=",
                "AWS_SECRET_ACCESS_KEY=",
                "AWS_DEFAULT_REGION=us-east-1",
                "DATA_SOURCE_S3_BUCKET=",
                "DATA_SOURCE_S3_PREFIX=",
            ],
        )
        if c.data_source == "minio":
            lines.append("DATA_SOURCE_S3_ENDPOINT_URL=http://localhost:9000")
        elif c.data_source == "ceph_s3":
            lines.append("DATA_SOURCE_S3_ENDPOINT_URL=https://rgw.example.com")

    if c.data_source == "azure_blob":
        lines.extend(
            [
                "AZURE_STORAGE_ACCOUNT_NAME=",
                "AZURE_STORAGE_CONTAINER=",
                "AZURE_STORAGE_PREFIX=",
                "# Auth: connection string OR (AZURE_CLIENT_ID + tenant) via DefaultAzureCredential",
                "AZURE_STORAGE_CONNECTION_STRING=",
            ],
        )

    if c.data_source == "gcs":
        lines.extend(
            [
                "GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json",
                "DATA_SOURCE_GCS_BUCKET=",
                "DATA_SOURCE_GCS_PREFIX=",
            ],
        )

    if c.data_source == "gdrive":
        lines.extend(
            [
                "# OAuth or service account — see tools/data_source/google_drive.py",
                "GOOGLE_DRIVE_FOLDER_ID=",
                "GOOGLE_APPLICATION_CREDENTIALS=",
            ],
        )

    if c.data_source == "onedrive":
        lines.extend(
            [
                "# MSAL — see tools/data_source/onedrive.py",
                "AZURE_CLIENT_ID=",
                "AZURE_TENANT_ID=",
                "ONEDRIVE_FOLDER_PATH=/drive/root:/RAG/corpus",
            ],
        )

    lines.extend(
        [
            "",
            "# --- Vector store (ai_builder.tools.vector_store — faiss/chroma/qdrant built-in) ---",
            f"VECTOR_PROVIDER={c.vector_backend}",
            "VECTOR_STORE_PATH=data/vectorstore",
            "VECTOR_COLLECTION_NAME=default",
            "CHROMA_HOST=localhost",
            "CHROMA_PORT=8000",
            "QDRANT_URL=http://localhost:6333",
            "# Extended backends (opensearch, milvus, …): set client URLs for your own wiring.",
            "OPENSEARCH_URL=http://localhost:9200",
            "MILVUS_URI=http://localhost:19530",
            "WEAVIATE_URL=http://localhost:8080",
            "REDIS_URL=redis://localhost:6379/0",
            "LANCEDB_URI=.lancedb",
            "POSTGRES_VECTOR_URL=postgresql://user:pass@localhost:5432/db",
            "",
            "# Langfuse — traces from Tracer / configure_tracing_from_env()",
            "LANGFUSE_PUBLIC_KEY=",
            "LANGFUSE_SECRET_KEY=",
            "LANGFUSE_HOST=https://cloud.langfuse.com",
            "LANGFUSE_ENABLED=true",
            "",
        ],
    )
    return "\n".join(lines)


def config_defaults_for_template(choices: RagScaffoldChoices | None) -> tuple[str, str, str, str]:
    """Defaults for generated config.py: vector_provider, data_source_type, qdrant_url, embedding_model_id."""
    c = choices or RagScaffoldChoices.non_interactive_default()
    vp = c.vector_backend if c.vector_backend != "none" else "faiss"
    ds = c.data_source
    em = c.embedding_model_id
    return vp, ds, "http://localhost:6333", em

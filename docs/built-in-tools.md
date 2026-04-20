# Built-in tools

All tools live under **`ai_builder.tools`**. Import from the umbrella package:

```python
from ai_builder.tools import DocumentLoader, TextSplitter
```

Heavy dependencies are **optional** — install **`ai-builder[docs]`**, **`[rag]`**, **`[embeddings-local]`**, **`[llm]`**, **`[faiss]`**, **`[chroma]`**, **`[qdrant]`**, **`data-s3`**, **`vector-opensearch`**, **`[search]`**, or bundles as needed.

---

## Document loading

**`DocumentLoader`** walks a directory and dispatches per file extension into format-specific loaders (PDF, DOCX, TXT, MD, HTML, RTF, spreadsheets, JSON, XML, …).

Optional parsers (PDF, Office, HTML, …) typically require **`ai-builder[docs]`** or granular extras (**`docs-pdf`**, **`docs-word`**, …).

Granular loaders (PDF-only, Word-only, …) are exposed as separate classes — see **`ai-builder add`** and package **`ai_builder.tools.document_loader`**.

---

## Data sources (`ai_builder.tools.data_source`)

Resolve **where documents live** before **`DocumentLoader`** runs:

| Tool | Purpose |
|------|---------|
| **`LocalFilesystemDataSource`** | **`DATA_SOURCE_LOCAL_PATH`** must be an **absolute** directory (use for **EFS** when mounted). |
| **`S3DataSource`**, **`MinioDataSource`**, **`CephRgwDataSource`** | Sync a bucket prefix to a temp dir (**`boto3`**; set **`DATA_SOURCE_S3_ENDPOINT_URL`** for MinIO/Ceph). |
| **`AzureBlobDataSource`**, **`GcsDataSource`** | Sync blob prefix to a temp dir. |
| **`GoogleDriveDataSource`**, **`OneDriveDataSource`** | Stub entry points — install **`data-gdrive`** / **`data-onedrive`** and implement OAuth in your app. |

Imports: **`from ai_builder.tools import LocalFilesystemDataSource, S3DataSource`** (see **`ai_builder.tools.data_source`**).

---

## Text splitting

**`TextSplitter`** recursively splits loaded documents into overlapping chunks with metadata (**`chunk_id`** when enabled). Configure via **`SplitterConfig`** (chunk size, overlap, separators).

---

## Embeddings

**`Embedder`** uses **sentence-transformers** when installed. Models are selectable via configuration / env (see **`EmbedderConfig`**).

**`ai_builder.tools.embeddings`** exposes one preset **`Embedder`** per supported Hugging Face id (**`TOOLS_BY_MODEL_ID`** / **`get_preset_embedder`**). **`ai-builder create rag`** writes a matching **`embed-model-<slug>`** optional extra in the generated **`pyproject.toml`** so **`uv pip install -e ".[embed-model-…]"`** installs only that model’s pip set ( **`BAAI/bge-m3`** also pulls **`sentencepiece`**).

Requires optional **`sentence-transformers`** (**`ai-builder[embeddings-local]`** or **`[rag]`**). For OpenAI embedding *client* workflows only: **`embeddings-openai`**.

---

## Vector stores

**`VectorStoreWriter`** indexes embedded chunks into:

| Provider | Notes |
|----------|--------|
| **faiss** | Local files under `store_path`; requires **`faiss-cpu`** (**`ai-builder[faiss]`**). |
| **chroma** | HTTP client; **`chromadb`**. |
| **qdrant** | **`qdrant_url`** — **`qdrant-client`**. |

Optional **prebuilt tool instances**: **`ai_builder.tools.vector_store.faiss_tool`**, **`qdrant_tool`**, **`chroma_tool`** (each wraps **`VectorStoreWriter`** with a fixed provider).

**Other backends** (OpenSearch, Milvus, Weaviate, Postgres+pgvector, Redis, LanceDB, Vald, …): install **`vector-opensearch`**, **`vector-milvus`**, etc., and wire your own indexing — **`Retriever`** / **`VectorStoreWriter`** only implement **faiss / chroma / qdrant** today.

---

## Retrieval

**`Retriever`** queries **FAISS / Chroma / Qdrant** using the configured embedding model. **`provider`** is a string — unsupported values fail at runtime with an explicit error until you add integration code.

---

## LLM

**`LLMTool`** and connector helpers target OpenAI, Anthropic, Ollama, Azure, Bedrock, etc., when **`ai-builder[llm]`** (or provider-specific packages) are installed.

---

## Web search

**`WebSearchTool`** integrates with **Tavily** when **`tavily-python`** / **`ai-builder[search]`** is available.

---

## Further reading

- Source layout: **`src/tools/`** (import path **`ai_builder.tools`**)
- On-demand integration: **`ai-builder add <tool-name>`** ([CLI reference](cli-reference.md))

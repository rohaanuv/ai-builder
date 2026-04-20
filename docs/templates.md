# Templates (`ai-builder create`)

Each template is a generator under **`ai_builder/templates/`**. Generated projects share common pieces: **`pyproject.toml`**, **`pipeline.yaml`**, **`Dockerfile`**, **`docker-compose.yml`**, **`tests/`**, and often **`k8s/`**.

Python requirement for scaffolds: **≥ 3.13** (as written in generated `pyproject.toml`).

---

## `create tool`

**Purpose:** Single composable **`BaseTool`** with **`src/<pkg>/main.py`** exporting **`tool`**.

**Typical files:** `config.py`, `tests/`, deployment stubs.

**Run:** `ai-builder run . --input "..."` when **`main.py`** exposes **`tool`**.

---

## `create rag`

**Purpose:** Retrieval-oriented pipeline using **`ai_builder.tools`** (loader, splitter, embedder, vector store, retriever).

**Interactive wizard (default):** On a TTY, **`ai-builder create rag <name>`** prompts for:

1. **Data source** — local/EFS path, S3, Azure Blob, GCS, Google Drive / OneDrive (stubs), MinIO, Ceph RGW — updates **`requirements.txt`** with clients (**`boto3`**, **`azure-storage-blob`**, …) and fills **`DATA_SOURCE_*`** in **`.env.example`**.
2. **Embeddings** — pick **one** Hugging Face **sentence-transformers** model from the numbered list (each maps to an **`embed-model-…`** optional extra); profile is always **local** ST embeddings + that **`EMBEDDING_MODEL_ID`**.
3. **Vector database** — none, FAISS, Qdrant, Chroma, or extended backends (OpenSearch, Milvus, Postgres+pgvector, …). **FAISS / Chroma / Qdrant** are implemented in **`VectorStoreWriter`** / **`Retriever`**; others install client libraries for your own indexing code.
4. **LLM provider** — optional **`llm-openai`**, **`llm-anthropic`**, **`llm-bedrock`**, Azure (no extra wheel).
5. **Document formats** — PDF, Word, slides, HTML, … (granular **`pdf`**, **`word`**, … extras).

Use **`--no-wizard`** to skip prompts ( **`requirements.txt`** keeps only core deps + comments). Non-TTY stdin also skips the wizard.

**Hello path:** **`DocumentLoader` | `TextSplitter`** only — runs without ML-heavy extras.

**Notable generated paths (current generator):**

- **`src/<pkg>/main.py`** — default **`ingest()`** demo.
- **`app/full_rag.py`** — optional full chain after installing **`embeddings-local`**, **`faiss`** or **`qdrant`**, etc.
- **`src/tools/data_source/`** — re-exports **`ai_builder.tools.data_source`** for your ingestion stage.
- **`src/<pkg>/workers/stage_runner.py`** — **`RAG_STAGE`** (`extract` / `chunk` / `embed`) for Kubernetes Jobs.
- **`docker-compose.yml`** — may include a **Qdrant** sidecar when generated with that layout.
- **`k8s/`** — namespace, PVCs, Qdrant deployment/service, Jobs; see **`k8s/README.md`** inside the generated project.

**Configuration:** Copy **`.env.example`** → **`.env`**; install **`uv pip install -e "."`** (and profile extras from the printed **`uv pip install -e ".[…]"`** line) before running scripts.

---

## `create agent-langchain`

**Purpose:** LangGraph-style agent layout with prompts and tool hooks.

**Extras:** LangChain-oriented optional dependencies; tracing via Langfuse when configured.

---

## `create agent-deep`

**Purpose:** Multi-agent “research” style scaffold (supervisor / workers pattern) using **`AgentBus`**.

**Extras:** Often **`search`** (Tavily) and LangChain stacks when enabled.

---

## `create pipeline`

**Purpose:** Generic **source → transform → sink** data pipeline with CSV/JSON examples and **`pipeline.yaml`** aligned with **`visualize`**.

---

## Optional extras per template

Use **`uv pip install -e ".[<extra>]"`** inside the generated project. Exact extras are listed in each project’s **`pyproject.toml`** and **`requirements.txt`** comments.

Global catalog for adding tools to an existing repo: **`ai-builder add`** (see [CLI reference](cli-reference.md)).

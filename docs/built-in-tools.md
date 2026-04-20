# Built-in tools

All tools live under **`ai_builder.tools`**. Import from the umbrella package:

```python
from ai_builder.tools import DocumentLoader, TextSplitter
```

Heavy dependencies are **optional** — install **`ai-builder[docs]`**, **`[rag]`**, **`[llm]`**, **`[chroma]`**, **`[qdrant]`**, **`[search]`**, or bundles as needed.

---

## Document loading

**`DocumentLoader`** walks a directory and dispatches per file extension into format-specific loaders (PDF, DOCX, TXT, MD, HTML, RTF, spreadsheets, JSON, XML, …).

Optional parsers (PDF, Office, HTML, …) typically require **`ai-builder[docs]`** or manual installs (`pdfplumber`, `python-docx`, …).

Granular loaders (PDF-only, Word-only, …) are exposed as separate classes — see **`ai-builder add`** and package **`ai_builder.tools.document_loader`**.

---

## Text splitting

**`TextSplitter`** recursively splits loaded documents into overlapping chunks with metadata (**`chunk_id`** when enabled). Configure via **`SplitterConfig`** (chunk size, overlap, separators).

---

## Embeddings

**`Embedder`** uses **sentence-transformers** when installed. Models are selectable via configuration / env (see **`EmbedderConfig`**).

Requires optional **`sentence-transformers`** / **`ai-builder[rag]`**-style installs.

---

## Vector stores

**`VectorStoreWriter`** indexes embedded chunks into:

| Provider | Notes |
|----------|--------|
| **faiss** | Local files under `store_path`; requires **`faiss-cpu`** (or similar). |
| **chroma** | Remote or embedded Chroma client. |
| **qdrant** | **`qdrant_url`** — requires **`qdrant-client`**. |

---

## Retrieval

**`Retriever`** queries the same backend types as the writer (FAISS / Chroma / Qdrant) using the configured embedding model.

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

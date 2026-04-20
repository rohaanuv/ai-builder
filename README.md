# ai-builder

Lightweight CLI and library for **composable AI tools, agents, and pipelines** (Python **3.13+**, Pydantic-typed).

## Documentation

- **[Full documentation index](https://github.com/rohaanuv/ai-builder/blob/main/docs/README.md)** (`docs/` in the repo)
- **[Single-page overview](https://github.com/rohaanuv/ai-builder/blob/main/README.md)** at repository root

## Install

```bash
pip install "git+https://github.com/rohaanuv/ai-builder.git"
```

Upgrades:

```bash
pip install --upgrade "git+https://github.com/rohaanuv/ai-builder.git"
```

With extras:

```bash
pip install "ai-builder[rag,tracing] @ git+https://github.com/rohaanuv/ai-builder.git"
```

Document loaders use **optional** dependencies (only formats you install can be extracted):

| Extra | Formats |
| --- | --- |
| `docs-pdf` | `.pdf` |
| `docs-word` | `.docx`, `.dotx`, legacy `.doc`/`.dot` |
| `docs-slides` | `.pptx` |
| `docs-html` | `.html`, `.htm` |
| `docs-rtf` | `.rtf` |
| `docs-spreadsheet` | `.xlsx`, `.xls` |
| `docs-epub` | `.epub` |
| `docs-odt` | `.odt` (OpenDocument text) |
| `docs` | all of the above |

Embeddings: `embeddings-local` (sentence-transformers), `embeddings-openai` (OpenAI client for custom API flows). LLM: `llm-openai`, `llm-anthropic`, `llm-bedrock`, or combined `llm`.

Example: `pip install "ai-builder[docs-pdf] @ git+https://github.com/rohaanuv/ai-builder.git"` for PDFs only.

## CLI

```bash
ai-builder create rag my-app   # wizard: data source, embeddings, vector DB, LLM, formats
# ai-builder create rag my-app --no-wizard   # skip prompts (comment-only requirements.txt)

cd my-app && uv venv --python 3.13 .venv && source .venv/bin/activate
cp .env.example .env && uv pip install -e "."
python -m my_app
```

`ai_builder.tools.data_source` — local/EFS path, S3 (incl. MinIO, Ceph RGW), Azure Blob, GCS; Google Drive & OneDrive are stub entry points (install extras, then implement OAuth in your app).  
`ai_builder.tools.vector_store` — FAISS, Chroma, and Qdrant are fully implemented; other vector clients are optional dependencies for you to wire to your index.

## License

AGPL-3.0-or-later — see [LICENSE](LICENSE).

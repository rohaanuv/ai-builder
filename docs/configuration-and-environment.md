# Configuration and environment

## `BaseConfig`

Projects subclass **`BaseConfig`** from **`ai_builder.core.config`**:

```python
from pathlib import Path
from pydantic import Field
from ai_builder.core.config import BaseConfig

class AppConfig(BaseConfig):
    chunk_size: int = Field(default=1000)
    qdrant_url: str = Field(default="http://localhost:6333")
    data_dir: Path = Path("data")
```

**`BaseSettings`** behavior:

- Reads **`.env`** from the working directory (**`env_file=".env"`**).
- **`extra = "ignore"`** — unknown env vars do not crash the model.

Field names map to environment variables via pydantic-settings conventions (typically **upper snake** env keys).

---

## `.env` vs `.env.example`

Scaffolds often ship **`.env.example`** (safe to commit). Copy:

```bash
cp .env.example .env
```

Never commit secrets (API keys, Langfuse secrets, cloud credentials).

---

## Typical variables (examples)

Names vary per scaffold; consult your project’s **`README.md`** and **`config.py`**.

| Concern | Example variables |
|---------|---------------------|
| Logging | **`LOG_LEVEL`** |
| Chunking | **`CHUNK_SIZE`**, **`CHUNK_OVERLAP`** |
| Langfuse | **`LANGFUSE_PUBLIC_KEY`**, **`LANGFUSE_SECRET_KEY`**, **`LANGFUSE_HOST`**, **`LANGFUSE_ENABLED`** |
| Vector DB | **`VECTOR_PROVIDER`**, **`QDRANT_URL`** |
| LLMs | Provider-specific (`OPENAI_API_KEY`, …) |

---

## Docker and Kubernetes

- **Docker Compose** often references **`env_file: .env`** — create `.env` before **`docker compose up`**.
- **Kubernetes:** use **`ConfigMap`** / **`Secret`** instead of committing `.env`; generated RAG manifests may include a starter ConfigMap — override for production.

See [Deployment](deployment.md).

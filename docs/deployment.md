# Deployment

Generated projects include files produced by **`ai_builder.deploy.generators`** (Dockerfile, Compose, Kubernetes manifests). Exact layout depends on template and generator version.

## Docker image

Typical **`Dockerfile`** traits:

- Base **`python:3.13-slim`** (or similar).
- Installs **`requirements.txt`** / **`pyproject.toml`** dependencies.
- Copies source and runs **`pip install -e .`** so the scaffold package imports correctly.
- Sets **`PYTHONUNBUFFERED`** and optional model cache dirs (**`HF_HOME`**).

Build:

```bash
docker build -t myapp:latest .
```

## Docker Compose

**`docker-compose.yml`** may define:

- The application service building from the repo root.
- Volume mounts for **`./data`** and embedding caches.
- Optionally a **Qdrant** (or other) sidecar when generated for RAG-style layouts.

Requirements:

- Create **`.env`** locally (often copy from **`.env.example`**).
- Ensure **`VECTOR_PROVIDER`** / **`QDRANT_URL`** align with Compose services.

```bash
docker compose up --build
```

## Kubernetes

RAG-oriented scaffolds may emit:

- **`Namespace`**
- **PVCs** for staging checkpoints and vector DB storage
- **`ConfigMap`** defaults (non-secret)
- **Qdrant `Deployment`** + **`Service`**
- **`Job`** manifests per pipeline stage (**extract / chunk / embed**) calling **`python -m <pkg>.workers.stage_runner`**

Read **`k8s/README.md`** inside your generated project for ordering (**extract → chunk → embed**), **`kubectl wait`**, and PVC access mode notes (**ReadWriteOnce** vs shared storage).

Use **Secrets** for Langfuse keys and cloud credentials instead of plain ConfigMaps in production.

---

## Related

- [Installation and upgrade](installation-and-upgrade.md)
- [Templates — RAG](templates.md#create-rag)

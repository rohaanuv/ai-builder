# Observability (tracing and Langfuse)

The **`ai_builder.tracing`** package collects spans during tool and pipeline execution and can export them to **Langfuse**.

## API surface

```python
from ai_builder.tracing import (
    Tracer,
    configure_tracing_from_env,
    trace,
    traced_tool,
    traced_pipeline,
)
```

### Environment-driven setup

Call early in **`main`** or stage workers:

```python
from ai_builder.tracing import Tracer, configure_tracing_from_env

configure_tracing_from_env()
Tracer.new_trace("my-run")
try:
    ...
finally:
    Tracer.flush()
```

### Manual configuration

```python
Tracer.configure(backend="langfuse", public_key="pk-...", secret_key="sk-...")
```

### Decorators and helpers

- **`@trace("operation-name")`** — wrap functions.
- **`traced_tool`**, **`traced_pipeline`** — attach tracing to **`BaseTool`** / **`Pipeline`** instances.

See **`tracing/tracer.py`** for **`Tracer.span`** context managers.

---

## Langfuse (cloud or self-hosted)

Set environment variables (typically in **`.env`**):

```env
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_HOST=https://cloud.langfuse.com
LANGFUSE_ENABLED=true
```

For **self-hosted** Langfuse, point **`LANGFUSE_HOST`** at your deployment URL.

Ensure the **`langfuse`** dependency is installed (included in many scaffolds; globally via **`pip install 'ai-builder[tracing] @ git+…'`**).

---

## Troubleshooting

- No traces appear — confirm **`configure_tracing_from_env()`** runs before work, **`Tracer.flush()`** runs after, and keys/host are correct.
- Import errors — install **`tracing`** extra or **`pip install langfuse`**.

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

## CLI

```bash
ai-builder create rag my-app
cd my-app && uv venv --python 3.13 .venv && source .venv/bin/activate
cp .env.example .env && uv pip install -e "."
python -m my_app
```

## License

AGPL-3.0-or-later — see [LICENSE](../LICENSE).

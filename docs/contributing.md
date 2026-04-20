# Contributing

## Clone and editable install

```bash
git clone https://github.com/rohaanuv/ai-builder.git
cd ai-builder
uv venv --python 3.13 .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
uv pip install -e ".[all,dev]"
```

Run **`ai-builder`** from this environment while developing (`pip install -e .` wires the CLI).

---

## Guidelines

- Match existing style (Ruff-enforced line length where configured).
- Prefer **`uv`** for environments consistent with **`AGENTS.md`**.
- Framework changes belong under **`src/`** (logical package **`ai_builder`**). New subpackages need an entry in **`pyproject.toml`** under **`[tool.setuptools]`** → **`packages`**.
- Bump **`pyproject.toml`** **`version`** for releases you publish.

---

## Documentation

Multi-page docs live in **`docs/`** ([index](README.md)); the root **`README.md`** stays a concise front door.

---

## License

Contributions are accepted under **[AGPL-3.0](../LICENSE)** — network use triggers source-sharing obligations when you modify and deploy the software.

"""Interactive dependency selection for `ai-builder create rag`."""

from __future__ import annotations

import sys

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, IntPrompt

from ai_builder.templates.rag_scaffold import (
    DEFAULT_EMBEDDING_MODEL_ID,
    FORMAT_GROUPS,
    DataSourceChoice,
    EmbeddingChoice,
    LlmChoice,
    RagScaffoldChoices,
    VectorBackendChoice,
    selected_uv_extras,
)
from ai_builder.tools.embeddings.config import SUPPORTED_MODELS
from ai_builder.tools.embeddings.registry import EMBEDDING_EXTRA_BY_MODEL

console = Console(stderr=True)


def _ask_data_source() -> DataSourceChoice:
    console.print(
        "\n[bold]Data source[/bold] (where raw documents live; see [cyan]ai_builder.tools.data_source[/cyan])\n"
        "  0 = local filesystem — [dim]absolute path in env[/dim]\n"
        "  1 = AWS EFS — [dim]same as local, use EFS mount path[/dim]\n"
        "  2 = AWS S3 (or S3-compatible via env)\n"
        "  3 = Azure Blob Storage\n"
        "  4 = Google Cloud Storage\n"
        "  5 = Google Drive (OAuth / API — stub in package)\n"
        "  6 = OneDrive (MSAL — stub in package)\n"
        "  7 = MinIO (self-hosted, S3 API)\n"
        "  8 = Ceph RGW (S3 API)\n",
    )
    c = IntPrompt.ask("Choice", default=0, show_default=True)
    return {
        0: "local",
        1: "efs",
        2: "s3",
        3: "azure_blob",
        4: "gcs",
        5: "gdrive",
        6: "onedrive",
        7: "minio",
        8: "ceph_s3",
    }.get(max(0, min(c, 8)), "local")


def _ask_embedding() -> EmbeddingChoice:
    console.print(
        "\n[bold]Embeddings[/bold] (indexing / vector search)\n"
        "  0 = none (loader + splitter only)\n"
        "  1 = local — [cyan]sentence-transformers[/cyan] (built-in Embedder)\n"
        "  2 = OpenAI API — [cyan]openai[/cyan] (custom embedding calls only)\n",
    )
    c = IntPrompt.ask("Choice", default=1, show_default=True)
    if c == 0:
        return "none"
    if c == 2:
        return "openai_api"
    return "local"


def _ask_embedding_model_id() -> str:
    """Pick a sentence-transformers model (``SUPPORTED_MODELS`` in ``embeddings.config``)."""
    models = list(SUPPORTED_MODELS.keys())
    console.print(
        Panel.fit(
            "[bold]Pick exactly one Hugging Face model[/bold] — your generated "
            "[cyan]pyproject.toml[/cyan] gets a matching optional extra "
            "(e.g. [green]embed-model-baai-bge-m3[/green]) so "
            "[cyan]uv pip install -e \".[…]\"[/cyan] installs only that stack.\n\n"
            "Same id is written to [cyan]EMBEDDING_MODEL_ID[/cyan] in [cyan].env.example[/cyan] "
            "for [cyan]Embedder[/cyan] / [cyan]Retriever[/cyan].",
            title="Local embeddings model",
            border_style="magenta",
        ),
    )
    console.print(
        "\n[bold]Models[/bold] — [cyan]sentence-transformers[/cyan]\n",
    )
    for i, mid in enumerate(models, start=1):
        meta = SUPPORTED_MODELS[mid]
        extra = EMBEDDING_EXTRA_BY_MODEL.get(mid, "")
        extra_line = f"\n      [dim]uv extra:[/dim] [green]{extra}[/green]" if extra else ""
        console.print(
            f"  {i:2} = [cyan]{mid}[/cyan]{extra_line}\n"
            f"      [dim]dim={meta['dim']}, max_seq={meta['max_seq']}[/dim]",
        )
    c = IntPrompt.ask("Choice", default=1, show_default=True)
    idx = max(1, min(int(c), len(models))) - 1
    return models[idx]


def _ask_vector_backend() -> VectorBackendChoice:
    console.print(
        "\n[bold]Vector database[/bold] ([cyan]faiss[/cyan]/[cyan]chroma[/cyan]/[cyan]qdrant[/cyan] "
        "integrated in ai-builder; others = client libs + your wiring)\n"
        "  0 = none\n"
        "  1 = FAISS\n"
        "  2 = Qdrant\n"
        "  3 = Chroma\n"
        "  4 = OpenSearch\n"
        "  5 = Milvus\n"
        "  6 = MongoDB\n"
        "  7 = Postgres (+ pgvector)\n"
        "  8 = Weaviate\n"
        "  9 = Vald\n"
        "  10 = Redis\n"
        "  11 = LanceDB\n",
    )
    c = IntPrompt.ask("Choice", default=1, show_default=True)
    return {
        0: "none",
        1: "faiss",
        2: "qdrant",
        3: "chroma",
        4: "opensearch",
        5: "milvus",
        6: "mongodb",
        7: "postgres",
        8: "weaviate",
        9: "vald",
        10: "redis",
        11: "lancedb",
    }.get(max(0, min(c, 11)), "faiss")


def _ask_llm() -> LlmChoice:
    console.print(
        "\n[bold]LLM provider[/bold] (generation — matches ai_builder.tools.llm)\n"
        "  0 = none\n"
        "  1 = OpenAI-compatible SDK ([cyan]openai[/cyan])\n"
        "  2 = Anthropic ([cyan]anthropic[/cyan])\n"
        "  3 = AWS Bedrock ([cyan]anthropic[/cyan] AnthropicBedrock)\n"
        "  4 = Azure OpenAI ([dim]stdlib HTTP in ai-builder[/dim])\n",
    )
    c = IntPrompt.ask("Choice", default=0, show_default=True)
    return {
        0: "none",
        1: "openai",
        2: "anthropic",
        3: "bedrock",
        4: "azure",
    }.get(max(0, min(c, 4)), "none")


def _ask_formats(chosen: set[str]) -> None:
    console.print(
        "\n[bold]Document formats[/bold] (TXT/MD/CSV/JSON/XML need no extra packages).\n",
    )
    labels = [
        ("pdf", "PDF"),
        ("word", "Word — .docx / legacy .doc"),
        ("slides", "PowerPoint — .pptx"),
        ("html", "HTML / HTM"),
        ("rtf", "RTF"),
        ("spreadsheet", "Spreadsheet — .xlsx / .xls"),
        ("epub", "EPUB"),
        ("odt", "OpenDocument — .odt"),
    ]
    for key, label in labels:
        if Confirm.ask(f"Include [bold]{label}[/bold]?", default=key in chosen):
            chosen.add(key)
        else:
            chosen.discard(key)


def prompt_rag_choices() -> RagScaffoldChoices:
    console.print(
        Panel.fit(
            "[bold]Configure dependencies[/bold]\n"
            "Updates [cyan]requirements.txt[/cyan], [cyan].env.example[/cyan], "
            "and prints [cyan]uv pip install -e \".[…]\"[/cyan].",
            title="ai-builder create rag",
        ),
    )

    data_source = _ask_data_source()
    embedding = _ask_embedding()
    if embedding == "local":
        embedding_model_id = _ask_embedding_model_id()
    else:
        embedding_model_id = DEFAULT_EMBEDDING_MODEL_ID
    vector_backend = _ask_vector_backend()
    llm = _ask_llm()

    if Confirm.ask("\nCustomize document format libraries (default = all)?", default=False):
        formats: set[str] = set()
        _ask_formats(formats)
    else:
        formats = set(FORMAT_GROUPS)

    choices = RagScaffoldChoices(
        data_source=data_source,
        embedding=embedding,
        embedding_model_id=embedding_model_id,
        vector_backend=vector_backend,
        llm=llm,
        formats=frozenset(formats),
    )

    extras = ",".join(selected_uv_extras(choices))
    console.print(f"\n[green]Profile extras:[/green] [cyan]{extras}[/cyan]")
    console.print("[dim]Equivalent install:[/dim]")
    console.print(f'  uv pip install -e ".[{extras}]"\n')

    return choices


def prompt_rag_choices_optional(use_wizard: bool) -> RagScaffoldChoices | None:
    """Return None only for explicit ``--no-wizard`` (minimal requirements.txt)."""
    if not use_wizard:
        return None
    # IDE / piped / CI: cannot prompt — use a full default profile (not empty comments).
    if not sys.stdin.isatty():
        console.print(
            "[yellow]Not an interactive terminal — using default dependency profile "
            "(install ai-builder from source / upgrade if prompts never appear).[/yellow]",
        )
        return RagScaffoldChoices.non_interactive_default()
    return prompt_rag_choices()

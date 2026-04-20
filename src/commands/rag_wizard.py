"""Interactive dependency selection — **only** for ``ai-builder create rag``.

Other commands (``create tool``, ``create pipeline``, ``create agent-*``) do not use this wizard;
they scaffold with fixed templates. Only ``create rag`` reads these prompts to fill
``pyproject.toml`` / ``requirements.txt`` / ``.env.example``.
"""

from __future__ import annotations

import sys

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, IntPrompt

from ai_builder.templates.rag_scaffold import (
    FORMAT_GROUPS,
    DataSourceChoice,
    EmbeddingChoice,
    LlmChoice,
    RagScaffoldChoices,
    VectorBackendChoice,
    selected_uv_extras,
)
from ai_builder.tools.embeddings.config import SUPPORTED_MODELS

# Use stdout so prompts align with Typer/Rich CLI output from ``create rag`` (same stream as version line).
console = Console()


def _embedding_model_ids_ordered() -> list[str]:
    """Stable order — matches ``SUPPORTED_MODELS`` insertion order in ``embeddings.config``."""
    return list(SUPPORTED_MODELS.keys())


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
    c = IntPrompt.ask("Data source", default=0, show_default=True)
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


def _ask_embeddings_sentence_transformers() -> tuple[EmbeddingChoice, str]:
    """
    Pick sentence-transformers model by index — always ``local`` embeddings + chosen HF id.

    Options are exactly ``SUPPORTED_MODELS`` keys (see ``embeddings.config``).
    """
    models = _embedding_model_ids_ordered()
    lo, hi = 1, len(models)
    console.print("\n[bold]Embeddings[/bold] (indexing / vector search)\n")
    for i, mid in enumerate(models, start=1):
        console.print(f"  {i}. [cyan]{mid}[/cyan]")
    console.print()
    console.print(
        "[dim]sentence-transformers · saved as [cyan]EMBEDDING_MODEL_ID[/cyan] · "
        "[cyan]pyproject.toml[/cyan] optional extra [green]embed-model-…[/green][/dim]\n",
    )
    c = IntPrompt.ask(f"Embeddings ({lo}–{hi})", default=1, show_default=True)
    idx = max(lo, min(int(c), hi)) - 1
    return "local", models[idx]


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
    c = IntPrompt.ask("Vector database", default=1, show_default=True)
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
        Panel.fit(
            "[bold]All LLM backends[/bold] match [cyan]Provider[/cyan] in "
            "[cyan]ai_builder.tools.llm.config[/cyan] and connectors under "
            "[cyan]ai_builder.tools.llm.connectors[/cyan].",
            title="LLM providers",
            border_style="green",
        ),
    )
    console.print(
        "\n[bold]LLM provider[/bold] (generation)\n"
        "  0 = none\n"
        "  1 = OpenAI-compatible SDK ([cyan]openai[/cyan]) — OpenAI or compatible HTTP APIs\n"
        "  2 = Anthropic ([cyan]anthropic[/cyan]) — Messages API\n"
        "  3 = AWS Bedrock ([cyan]bedrock[/cyan]) — Claude via Bedrock\n"
        "  4 = Azure OpenAI ([cyan]azure[/cyan]) — API key or OAuth-style auth\n"
        "  5 = Ollama ([cyan]ollama[/cyan]) — local server, stdlib HTTP in LLMTool\n"
        "  6 = Self-hosted OpenAI-compatible ([cyan]self_hosted[/cyan]) — vLLM, LiteLLM, …\n",
    )
    c = IntPrompt.ask("LLM provider", default=0, show_default=True)
    return {
        0: "none",
        1: "openai",
        2: "anthropic",
        3: "bedrock",
        4: "azure",
        5: "ollama",
        6: "self_hosted",
    }.get(max(0, min(c, 6)), "none")


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
            "[bold]Configure dependencies[/bold] for this RAG scaffold only.\n\n"
            "[dim]Applies to[/dim] [cyan]ai-builder create rag <name>[/cyan] [dim]— not[/dim] "
            "[cyan]create tool[/cyan][dim],[/dim] [cyan]create pipeline[/cyan][dim], or[/dim] "
            "[cyan]create agent-*[/cyan][dim].[/dim]\n\n"
            "Updates [cyan]requirements.txt[/cyan], [cyan].env.example[/cyan], "
            "and prints [cyan]uv pip install -e \".[…]\"[/cyan].",
            title="create rag — dependency profile",
        ),
    )

    data_source = _ask_data_source()
    embedding, embedding_model_id = _ask_embeddings_sentence_transformers()
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

"""Core tracing engine with pluggable backends (console, Langfuse)."""

from __future__ import annotations

import functools
import logging
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Callable, Generator, Literal

logger = logging.getLogger(__name__)


@dataclass
class Span:
    """A single traced operation."""

    name: str
    trace_id: str = ""
    span_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    parent_id: str = ""
    start_time: float = field(default_factory=time.perf_counter)
    end_time: float = 0.0
    status: str = "running"
    input_data: Any = None
    output_data: Any = None
    metadata: dict[str, Any] = field(default_factory=dict)
    error: str | None = None

    @property
    def duration_ms(self) -> float:
        end = self.end_time or time.perf_counter()
        return round((end - self.start_time) * 1000, 2)

    def set_input(self, data: Any) -> None:
        self.input_data = data

    def set_output(self, data: Any) -> None:
        self.output_data = data

    def set_metadata(self, key: str, value: Any) -> None:
        self.metadata[key] = value

    def finish(self, status: str = "ok", error: str | None = None) -> None:
        self.end_time = time.perf_counter()
        self.status = status
        self.error = error

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_id": self.parent_id,
            "duration_ms": self.duration_ms,
            "status": self.status,
            "input": _safe_serialize(self.input_data),
            "output": _safe_serialize(self.output_data),
            "metadata": self.metadata,
            "error": self.error,
        }


class Tracer:
    """
    Singleton tracer that collects spans and exports to configured backend.

    Backends:
      - "console" (default): prints spans to stderr
      - "langfuse": exports to Langfuse server
    """

    _instance: Tracer | None = None
    _backend: Literal["console", "langfuse"] = "console"
    _langfuse_client: Any = None
    _langfuse_config: dict[str, str] = {}
    _spans: list[Span] = []
    _current_trace_id: str = ""

    @classmethod
    def configure(
        cls,
        backend: Literal["console", "langfuse"] = "console",
        **kwargs: str,
    ) -> None:
        """Configure the tracing backend.

        For Langfuse:
            Tracer.configure(
                backend="langfuse",
                public_key="pk-...",
                secret_key="sk-...",
                host="https://cloud.langfuse.com",  # optional
            )
        """
        cls._backend = backend
        cls._langfuse_config = kwargs
        cls._langfuse_client = None

        if backend == "langfuse":
            cls._init_langfuse()

        logger.info(f"Tracer configured: backend={backend}")

    @classmethod
    def _init_langfuse(cls) -> None:
        try:
            from langfuse import Langfuse

            cls._langfuse_client = Langfuse(
                public_key=cls._langfuse_config.get("public_key", ""),
                secret_key=cls._langfuse_config.get("secret_key", ""),
                host=cls._langfuse_config.get("host", "https://cloud.langfuse.com"),
            )
            logger.info("Langfuse client initialized")
        except ImportError:
            logger.warning("langfuse not installed. Install with: pip install langfuse")
            cls._backend = "console"

    @classmethod
    def new_trace(cls, name: str = "trace") -> str:
        """Start a new trace and return its ID."""
        cls._current_trace_id = uuid.uuid4().hex[:16]

        if cls._backend == "langfuse" and cls._langfuse_client:
            cls._langfuse_client.trace(id=cls._current_trace_id, name=name)

        return cls._current_trace_id

    @classmethod
    @contextmanager
    def span(cls, name: str, **meta: Any) -> Generator[Span, None, None]:
        """Context manager for a traced span."""
        if not cls._current_trace_id:
            cls.new_trace(name)

        s = Span(name=name, trace_id=cls._current_trace_id, metadata=meta)
        cls._spans.append(s)

        try:
            yield s
            s.finish("ok")
        except Exception as exc:
            s.finish("error", error=str(exc))
            raise
        finally:
            cls._export_span(s)

    @classmethod
    def _export_span(cls, s: Span) -> None:
        if cls._backend == "console":
            status_icon = "✓" if s.status == "ok" else "✗"
            logger.info(f"  [{status_icon}] {s.name} ({s.duration_ms:.0f}ms)")
        elif cls._backend == "langfuse" and cls._langfuse_client:
            try:
                lf_span = cls._langfuse_client.span(
                    trace_id=s.trace_id,
                    name=s.name,
                    input=_safe_serialize(s.input_data),
                    output=_safe_serialize(s.output_data),
                    metadata=s.metadata,
                    status_message=s.error,
                )
                if s.status == "error":
                    lf_span.update(level="ERROR")
            except Exception as exc:
                logger.warning(f"Langfuse export failed: {exc}")

    @classmethod
    def flush(cls) -> None:
        """Flush pending spans to the backend."""
        if cls._backend == "langfuse" and cls._langfuse_client:
            cls._langfuse_client.flush()

    @classmethod
    def get_spans(cls) -> list[dict[str, Any]]:
        """Return all collected spans as dicts."""
        return [s.to_dict() for s in cls._spans]

    @classmethod
    def reset(cls) -> None:
        """Clear all collected spans."""
        cls._spans.clear()
        cls._current_trace_id = ""


def configure_tracing_from_env() -> Literal["console", "langfuse"]:
    """Configure :class:`Tracer` from environment variables for Langfuse observability.

    When ``LANGFUSE_PUBLIC_KEY`` and ``LANGFUSE_SECRET_KEY`` are set, traces are sent to
    Langfuse. Otherwise spans use the console backend (log output).

    **Environment variables**

    - ``LANGFUSE_PUBLIC_KEY`` / ``LANGFUSE_SECRET_KEY`` — required for Langfuse
    - ``LANGFUSE_HOST`` — optional (default ``https://cloud.langfuse.com``)
    - ``LANGFUSE_ENABLED`` — set to ``false`` to force console-only even if keys exist
    """
    import os

    if os.getenv("LANGFUSE_ENABLED", "true").strip().lower() in (
        "0",
        "false",
        "no",
        "off",
    ):
        Tracer.configure(backend="console")
        return "console"

    pk = os.getenv("LANGFUSE_PUBLIC_KEY", "").strip()
    sk = os.getenv("LANGFUSE_SECRET_KEY", "").strip()
    host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com").strip()

    if pk and sk:
        Tracer.configure(
            backend="langfuse",
            public_key=pk,
            secret_key=sk,
            host=host,
        )
        logger.info("Tracer: Langfuse (from LANGFUSE_* environment variables)")
        return "langfuse"

    Tracer.configure(backend="console")
    return "console"


def trace(name: str) -> Callable:
    """Decorator: trace a function call as a span."""
    def decorator(fn: Callable) -> Callable:
        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            with Tracer.span(name) as s:
                s.set_input({"args_count": len(args), "kwargs": list(kwargs.keys())})
                result = fn(*args, **kwargs)
                s.set_output(_safe_serialize(result))
                return result
        return wrapper
    return decorator


def traced_tool(tool_instance: Any) -> Any:
    """Wrap a BaseTool so every .run() call is traced."""
    original_run = tool_instance.run

    @functools.wraps(original_run)
    def traced_run(inp: Any) -> Any:
        with Tracer.span(f"tool:{tool_instance.name}") as s:
            s.set_input(_safe_serialize(inp))
            result = original_run(inp)
            s.set_output(_safe_serialize(result))
            return result

    tool_instance.run = traced_run
    return tool_instance


def traced_pipeline(pipeline_instance: Any) -> Any:
    """Wrap a Pipeline so every step is traced."""
    for step in pipeline_instance.steps:
        traced_tool(step.tool)
    return pipeline_instance


def _safe_serialize(obj: Any) -> Any:
    """Safely serialize an object for tracing."""
    if obj is None:
        return None
    if isinstance(obj, (str, int, float, bool)):
        return obj
    if isinstance(obj, dict):
        return {k: _safe_serialize(v) for k, v in list(obj.items())[:20]}
    if isinstance(obj, (list, tuple)):
        return [_safe_serialize(x) for x in obj[:10]]
    if hasattr(obj, "model_dump"):
        try:
            d = obj.model_dump()
            if isinstance(d.get("data"), list) and len(d["data"]) > 5:
                d["data"] = d["data"][:5]
                d["_truncated"] = True
            return d
        except Exception:
            pass
    return str(obj)[:500]

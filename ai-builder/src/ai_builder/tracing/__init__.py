"""
ai_builder.tracing — observability for tools, agents, and pipelines.

Provides automatic tracing with optional Langfuse export.

Usage:
    from ai_builder.tracing import Tracer, trace

    # Decorator
    @trace("my-operation")
    def do_work():
        ...

    # Context manager
    with Tracer.span("embedding") as span:
        span.set_input({"texts": 100})
        result = embed(texts)
        span.set_output({"dimension": 384})

    # Export to Langfuse
    Tracer.configure(backend="langfuse", public_key="pk-...", secret_key="sk-...")
"""

from ai_builder.tracing.tracer import Tracer, Span, trace, traced_tool, traced_pipeline

__all__ = ["Tracer", "Span", "trace", "traced_tool", "traced_pipeline"]

"""
Agent-to-agent communication — message bus for composing multi-agent systems.

Supports:
  - Typed Pydantic messages between agents
  - Request/response pattern with correlation IDs
  - Pub/sub event broadcasting
  - Agent registration and discovery

Usage:
    bus = AgentBus()
    bus.register(agent_a)
    bus.register(agent_b)

    # Direct message
    response = bus.send(AgentMessage(
        sender="agent-a", receiver="agent-b",
        content={"query": "analyze this data"},
        message_type="request",
    ))

    # Broadcast
    bus.broadcast(AgentEvent(sender="agent-a", event="data_ready", payload={...}))
"""

from __future__ import annotations

import logging
import uuid
from collections import defaultdict
from typing import Any, Callable

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class AgentMessage(BaseModel):
    """Typed message for agent-to-agent communication."""

    id: str = Field(default_factory=lambda: uuid.uuid4().hex[:12])
    sender: str = Field(description="Name of the sending agent")
    receiver: str = Field(description="Name of the target agent")
    content: Any = Field(description="Message payload")
    message_type: str = Field(
        default="request",
        description="Message type: request, response, event, error",
    )
    correlation_id: str = Field(
        default="",
        description="Links a response to its original request",
    )
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = {"extra": "allow"}


class AgentEvent(BaseModel):
    """Broadcast event — no specific receiver."""

    id: str = Field(default_factory=lambda: uuid.uuid4().hex[:12])
    sender: str
    event: str = Field(description="Event name: data_ready, error, step_complete, etc.")
    payload: Any = Field(default=None)
    metadata: dict[str, Any] = Field(default_factory=dict)


class AgentCard(BaseModel):
    """Discovery card — describes an agent's capabilities (A2A-inspired)."""

    name: str
    description: str = ""
    version: str = "0.1.0"
    capabilities: list[str] = Field(default_factory=list)
    input_schema: dict[str, Any] = Field(default_factory=dict)
    output_schema: dict[str, Any] = Field(default_factory=dict)


MessageHandler = Callable[[AgentMessage], AgentMessage | None]
EventHandler = Callable[[AgentEvent], None]


class AgentBus:
    """
    In-process message bus for agent-to-agent communication.

    Agents register with a name and a handler. Messages route by receiver name.
    Events broadcast to all subscribers.

    For distributed agents, swap this with an HTTP/gRPC or MQ-backed bus.
    """

    def __init__(self) -> None:
        self._handlers: dict[str, MessageHandler] = {}
        self._event_handlers: dict[str, list[EventHandler]] = defaultdict(list)
        self._cards: dict[str, AgentCard] = {}
        self._history: list[AgentMessage | AgentEvent] = []

    def register(
        self,
        name: str,
        handler: MessageHandler,
        card: AgentCard | None = None,
    ) -> None:
        """Register an agent with a message handler."""
        self._handlers[name] = handler
        if card:
            self._cards[name] = card
        logger.info(f"AgentBus: registered '{name}'")

    def register_agent(self, agent: Any) -> None:
        """Register a BaseAgent instance — uses its name and creates a default handler."""
        from ai_builder.core.agent import BaseAgent, AgentInput

        if not isinstance(agent, BaseAgent):
            raise TypeError(f"Expected BaseAgent, got {type(agent)}")

        def handler(msg: AgentMessage) -> AgentMessage:
            query = msg.content if isinstance(msg.content, str) else str(msg.content)
            result = agent.run(query)
            return AgentMessage(
                sender=agent.name,
                receiver=msg.sender,
                content=result.model_dump(),
                message_type="response",
                correlation_id=msg.id,
            )

        card = AgentCard(
            name=agent.name,
            description=agent.description,
            version=agent.version,
        )
        self.register(agent.name, handler, card)

    def send(self, message: AgentMessage) -> AgentMessage | None:
        """Send a message to a specific agent. Returns the response (if any)."""
        self._history.append(message)
        handler = self._handlers.get(message.receiver)
        if not handler:
            logger.error(f"AgentBus: no handler for '{message.receiver}'")
            return AgentMessage(
                sender="bus",
                receiver=message.sender,
                content=f"Agent '{message.receiver}' not found",
                message_type="error",
                correlation_id=message.id,
            )

        logger.info(f"AgentBus: {message.sender} → {message.receiver} [{message.message_type}]")
        response = handler(message)
        if response:
            self._history.append(response)
        return response

    def subscribe(self, event_name: str, handler: EventHandler) -> None:
        """Subscribe to broadcast events."""
        self._event_handlers[event_name].append(handler)

    def broadcast(self, event: AgentEvent) -> None:
        """Broadcast an event to all subscribers."""
        self._history.append(event)
        logger.info(f"AgentBus: broadcast '{event.event}' from '{event.sender}'")
        for handler in self._event_handlers.get(event.event, []):
            try:
                handler(event)
            except Exception as exc:
                logger.error(f"Event handler failed: {exc}")

    def discover(self) -> list[AgentCard]:
        """List all registered agents and their capabilities."""
        return list(self._cards.values())

    @property
    def agents(self) -> list[str]:
        return list(self._handlers.keys())

    @property
    def history(self) -> list[AgentMessage | AgentEvent]:
        return self._history.copy()


# Global default bus (convenience)
default_bus = AgentBus()

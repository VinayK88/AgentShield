from dataclasses import dataclass, field
from typing import Any

@dataclass(frozen=True)
class ToolProfile:
    name: str
    read: bool = False
    write: bool = False
    external: bool = False
    sensitive: bool = False
    destructive: bool = False

@dataclass
class ToolCall:
    call_id: str
    agent_id: str
    user_intent: str
    tool: str
    action: str
    destination: str | None = None
    data_labels: list[str] = field(default_factory=list)
    untrusted_context: bool = False
    delegated_by: str | None = None
    args: dict[str, Any] = field(default_factory=dict)

@dataclass
class Decision:
    call_id: str
    decision: str
    risk_score: int
    reasons: list[str]
    redactions: list[str] = field(default_factory=list)
    policy_id: str = "AS-RUNTIME-001"

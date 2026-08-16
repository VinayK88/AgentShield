from __future__ import annotations
from collections import deque
from .models import ToolCall, ToolProfile, Decision

SENSITIVE_LABELS = {"PII", "PCI", "PHI", "SECRET", "CREDENTIAL"}

DEFAULT_TOOLS = {
    "search_web": ToolProfile("search_web", read=True, external=True),
    "read_customer_db": ToolProfile("read_customer_db", read=True, sensitive=True),
    "send_email": ToolProfile("send_email", write=True, external=True),
    "http_post": ToolProfile("http_post", write=True, external=True),
    "execute_sql": ToolProfile("execute_sql", read=True, write=True, sensitive=True),
    "delete_cloud_resource": ToolProfile("delete_cloud_resource", write=True, destructive=True),
}


class RuntimePolicyEngine:
    def __init__(self, tools: dict[str, ToolProfile] | None = None, history_size: int = 8):
        self.tools = tools or DEFAULT_TOOLS
        self.history: dict[str, deque[ToolCall]] = {}
        self.history_size = history_size

    def evaluate(self, call: ToolCall) -> Decision:
        tool = self.tools.get(call.tool)
        if not tool:
            return Decision(call.call_id, "BLOCK", 95, ["unknown or unregistered tool"])

        risk = 0
        reasons: list[str] = []
        redactions: list[str] = []

        if call.untrusted_context:
            risk += 25
            reasons.append("untrusted context influenced the proposed action")

        sensitive_labels = SENSITIVE_LABELS.intersection(call.data_labels)
        sensitive = bool(sensitive_labels)
        if sensitive:
            risk += 15
            reasons.append("sensitive data is present in the action context")

        if tool.external and sensitive:
            risk += 20
            reasons.append("sensitive data is moving toward an external destination")
            redactions.extend(sorted(sensitive_labels))

        intent = call.user_intent.lower()
        action = call.action.lower()
        if any(x in action for x in ("send", "post", "upload", "delete", "write")) and not any(
            x in intent for x in ("send", "share", "email", "upload", "delete", "write", "update")
        ):
            risk += 30
            reasons.append("observed action exceeds the declared user intent")

        if tool.destructive:
            risk += 45
            reasons.append("destructive tool requires explicit approval")

        if call.delegated_by and call.delegated_by == call.agent_id:
            risk += 20
            reasons.append("invalid self-delegation chain")

        prior = list(self.history.get(call.agent_id, []))
        if tool.external and any(self.tools.get(p.tool, ToolProfile("unknown")).sensitive for p in prior[-3:]):
            risk += 30
            reasons.append("sensitive-read → external-write trajectory detected")

        risk = min(risk, 100)
        if risk >= 80:
            decision = "BLOCK"
        elif risk >= 45:
            decision = "REQUIRE_APPROVAL"
        elif redactions:
            decision = "ALLOW_WITH_REDACTION"
        else:
            decision = "ALLOW"

        self._record(call)
        return Decision(call.call_id, decision, risk, reasons or ["request remains within runtime policy"], redactions)

    def _record(self, call: ToolCall) -> None:
        q = self.history.setdefault(call.agent_id, deque(maxlen=self.history_size))
        q.append(call)

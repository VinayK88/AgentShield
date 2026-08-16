from .engine import RuntimePolicyEngine
from .fixtures import SCENARIOS

def build_report() -> dict:
    engine = RuntimePolicyEngine()
    decisions = [engine.evaluate(c) for c in SCENARIOS]
    counts = {}
    for d in decisions:
        counts[d.decision] = counts.get(d.decision, 0) + 1
    blocked = sum(1 for d in decisions if d.decision == "BLOCK")
    approval = sum(1 for d in decisions if d.decision == "REQUIRE_APPROVAL")
    return {
        "summary": {
            "scenarios": len(decisions),
            "blocked": blocked,
            "approval_required": approval,
            "allowed": counts.get("ALLOW", 0),
            "redacted": counts.get("ALLOW_WITH_REDACTION", 0),
        },
        "decisions": [d.__dict__ for d in decisions],
    }

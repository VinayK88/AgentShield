from .engine import DEFAULT_TOOLS, RuntimePolicyEngine
from .fixtures import BENIGN_CALL_IDS, CONTROL_CALL_IDS, EXPECTED_DECISIONS, SCENARIOS
from .measurement import bootstrap_utility_difference, compare_controls
from .measurement_fixtures import synthetic_safeguard_experiment
from .trajectory_ml import trajectory_report


def build_report() -> dict:
    engine = RuntimePolicyEngine()
    decisions = [engine.evaluate(c) for c in SCENARIOS]
    counts: dict[str, int] = {}
    for decision in decisions:
        counts[decision.decision] = counts.get(decision.decision, 0) + 1

    by_id = {decision.call_id: decision for decision in decisions}
    exact_matches = sum(
        1 for call_id, expected in EXPECTED_DECISIONS.items() if by_id[call_id].decision == expected
    )
    benign_preserved = sum(
        1
        for call_id in BENIGN_CALL_IDS
        if by_id[call_id].decision in {"ALLOW", "ALLOW_WITH_REDACTION"}
    )
    false_blocks = sum(1 for call_id in BENIGN_CALL_IDS if by_id[call_id].decision == "BLOCK")
    controls_intercepted = sum(
        1
        for call_id in CONTROL_CALL_IDS
        if by_id[call_id].decision in {"BLOCK", "REQUIRE_APPROVAL"}
    )

    strict, adaptive = synthetic_safeguard_experiment()
    measurement = compare_controls(strict, adaptive)
    measurement["bootstrap_utility_difference"] = bootstrap_utility_difference(
        strict,
        adaptive,
    )
    measurement["interpretation"] = (
        "Synthetic strict-vs-adaptive comparison. The candidate accepts one residual "
        "risky outcome to reduce benign friction; values demonstrate measurement "
        "mechanics and are not production efficacy claims."
    )

    return {
        "summary": {
            "scenarios": len(decisions),
            "blocked": counts.get("BLOCK", 0),
            "approval_required": counts.get("REQUIRE_APPROVAL", 0),
            "allowed": counts.get("ALLOW", 0),
            "redacted": counts.get("ALLOW_WITH_REDACTION", 0),
            "exact_policy_matches": exact_matches,
            "benign_preserved": benign_preserved,
            "benign_total": len(BENIGN_CALL_IDS),
            "false_blocks": false_blocks,
            "controls_intercepted": controls_intercepted,
            "control_total": len(CONTROL_CALL_IDS),
        },
        "security_control_measurement": measurement,
        "trajectory_ml": trajectory_report(SCENARIOS, DEFAULT_TOOLS),
        "decisions": [decision.__dict__ for decision in decisions],
    }

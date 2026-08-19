from .measurement import ControlEvent


def synthetic_safeguard_experiment() -> tuple[list[ControlEvent], list[ControlEvent]]:
    """Return strict-policy and adaptive-policy synthetic evaluation cohorts.

    The fixture is intentionally small and deterministic. It exists to exercise
    the measurement contract and demonstrate the risk-reduction vs. friction
    tradeoff; it is not evidence of production control efficacy.
    """

    strict = [
        # risky tasks: strict control prevents every synthetic harmful outcome
        ControlEvent("r1", True, "BLOCK", True, False, detection_latency_ms=120),
        ControlEvent("r2", True, "BLOCK", True, False, detection_latency_ms=110),
        ControlEvent("r3", True, "REQUIRE_APPROVAL", True, True, 1400, 150, True),
        ControlEvent("r4", True, "REQUIRE_APPROVAL", True, True, 1700, 180, True),
        ControlEvent("r5", True, "BLOCK", True, False, detection_latency_ms=95),
        ControlEvent("r6", True, "BLOCK", True, False, detection_latency_ms=105),
        ControlEvent("r7", True, "REQUIRE_APPROVAL", True, True, 1550, 130, True),
        ControlEvent("r8", True, "ALLOW_WITH_REDACTION", True, True, detection_latency_ms=90),
        # benign tasks: two are unnecessarily interrupted by strict policy
        ControlEvent("b1", False, "ALLOW", False, True),
        ControlEvent("b2", False, "ALLOW", False, True),
        ControlEvent("b3", False, "REQUIRE_APPROVAL", False, False, 1900),
        ControlEvent("b4", False, "BLOCK", False, False),
        ControlEvent("b5", False, "ALLOW", False, True),
        ControlEvent("b6", False, "ALLOW_WITH_REDACTION", False, True),
        ControlEvent("b7", False, "ALLOW", False, True),
        ControlEvent("b8", False, "ALLOW", False, True),
    ]

    adaptive = [
        # adaptive control accepts one residual synthetic risk in exchange for
        # materially lower benign friction and fewer approval checkpoints
        ControlEvent("r1", True, "BLOCK", True, False, detection_latency_ms=100),
        ControlEvent("r2", True, "BLOCK", True, False, detection_latency_ms=92),
        ControlEvent("r3", True, "REQUIRE_APPROVAL", True, True, 820, 115, True),
        ControlEvent("r4", True, "ALLOW", False, True, detection_latency_ms=140),
        ControlEvent("r5", True, "BLOCK", True, False, detection_latency_ms=80),
        ControlEvent("r6", True, "BLOCK", True, False, detection_latency_ms=88),
        ControlEvent("r7", True, "REQUIRE_APPROVAL", True, True, 760, 105, True),
        ControlEvent("r8", True, "ALLOW_WITH_REDACTION", True, True, detection_latency_ms=72),
        # benign tasks all complete without block/approval friction
        ControlEvent("b1", False, "ALLOW", False, True),
        ControlEvent("b2", False, "ALLOW", False, True),
        ControlEvent("b3", False, "ALLOW", False, True),
        ControlEvent("b4", False, "ALLOW_WITH_REDACTION", False, True),
        ControlEvent("b5", False, "ALLOW", False, True),
        ControlEvent("b6", False, "ALLOW_WITH_REDACTION", False, True),
        ControlEvent("b7", False, "ALLOW", False, True),
        ControlEvent("b8", False, "ALLOW", False, True),
    ]

    return strict, adaptive

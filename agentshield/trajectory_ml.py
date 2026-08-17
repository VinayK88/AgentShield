from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
import math

from .models import ToolCall, ToolProfile

MODEL_NAME = "LaplaceMarkovTrajectoryModel"
MODEL_VERSION = "agentshield-trajectory-v1"

VOCABULARY = (
    "external_read",
    "internal_read",
    "sensitive_read",
    "external_write",
    "internal_write",
    "destructive_write",
    "unknown",
)

# Synthetic normal-reference tool trajectories. They encode ordinary task flow,
# not malicious examples, credentials, or live MCP traffic.
BENIGN_TRAJECTORIES = (
    ("external_read",),
    ("external_read", "external_read"),
    ("internal_read",),
    ("internal_read", "internal_read"),
    ("sensitive_read", "internal_read"),
    ("internal_read", "internal_write"),
    ("external_read", "internal_write"),
    ("internal_read", "external_read"),
    ("external_read", "external_write"),
    ("sensitive_read", "internal_write"),
)


@dataclass(frozen=True)
class TrajectoryFinding:
    call_id: str
    token: str
    sequence: tuple[str, ...]
    surprisal: float
    anomaly_percentile: float
    unusual_transition: str | None

    def to_dict(self) -> dict:
        return asdict(self)


class MarkovTrajectoryModel:
    def __init__(self, trajectories=BENIGN_TRAJECTORIES, alpha: float = 0.5):
        self.alpha = alpha
        self.start = Counter()
        self.transitions: dict[str, Counter] = defaultdict(Counter)
        self.vocabulary = tuple(VOCABULARY)
        for trajectory in trajectories:
            if not trajectory:
                continue
            self.start[trajectory[0]] += 1
            for left, right in zip(trajectory, trajectory[1:]):
                self.transitions[left][right] += 1
        self.reference_surprisal = tuple(self.surprisal(row) for row in trajectories if row)

    def _prob(self, counts: Counter, value: str) -> float:
        total = sum(counts.values())
        return (counts[value] + self.alpha) / (total + self.alpha * len(self.vocabulary))

    def surprisal(self, sequence: tuple[str, ...] | list[str]) -> float:
        if not sequence:
            return 0.0
        seq = tuple(sequence)
        log_prob = -math.log(self._prob(self.start, seq[0]))
        terms = 1
        for left, right in zip(seq, seq[1:]):
            log_prob += -math.log(self._prob(self.transitions[left], right))
            terms += 1
        return log_prob / terms

    def percentile(self, sequence: tuple[str, ...] | list[str]) -> float:
        score = self.surprisal(sequence)
        reference = self.reference_surprisal
        if not reference:
            return 0.0
        return 100.0 * sum(value <= score for value in reference) / len(reference)


def call_token(call: ToolCall, tools: dict[str, ToolProfile]) -> str:
    profile = tools.get(call.tool)
    if profile is None:
        return "unknown"
    if profile.destructive:
        return "destructive_write"
    if profile.write and profile.external:
        return "external_write"
    if profile.write:
        return "internal_write"
    if profile.read and profile.sensitive:
        return "sensitive_read"
    if profile.read and profile.external:
        return "external_read"
    if profile.read:
        return "internal_read"
    return "unknown"


def score_call(
    history: list[ToolCall],
    call: ToolCall,
    tools: dict[str, ToolProfile],
    model: MarkovTrajectoryModel | None = None,
) -> TrajectoryFinding:
    model = model or MarkovTrajectoryModel()
    recent = history[-4:]
    sequence = tuple(call_token(item, tools) for item in [*recent, call])
    percentile = round(model.percentile(sequence), 1)
    transition = None
    if len(sequence) >= 2:
        left, right = sequence[-2], sequence[-1]
        probability = model._prob(model.transitions[left], right)
        if probability < 0.12:
            transition = f"{left} -> {right}"
    return TrajectoryFinding(
        call_id=call.call_id,
        token=sequence[-1],
        sequence=sequence,
        surprisal=round(model.surprisal(sequence), 4),
        anomaly_percentile=percentile,
        unusual_transition=transition,
    )


def score_scenarios(calls: list[ToolCall], tools: dict[str, ToolProfile]) -> list[TrajectoryFinding]:
    model = MarkovTrajectoryModel()
    history: dict[str, list[ToolCall]] = defaultdict(list)
    rows = []
    for call in calls:
        rows.append(score_call(history[call.agent_id], call, tools, model))
        history[call.agent_id].append(call)
    return rows


def trajectory_report(calls: list[ToolCall], tools: dict[str, ToolProfile]) -> dict[str, object]:
    rows = score_scenarios(calls, tools)
    high = [row for row in rows if row.anomaly_percentile >= 90.0]
    return {
        "model": MODEL_NAME,
        "model_version": MODEL_VERSION,
        "training_sequences": len(BENIGN_TRAJECTORIES),
        "high_surprisal_calls": len(high),
        "findings": [row.to_dict() for row in rows],
        "boundary": "The learned sequence model is advisory. Deterministic runtime policy remains authoritative for ALLOW, REDACT, APPROVAL, and BLOCK decisions.",
    }

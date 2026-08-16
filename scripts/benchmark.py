import argparse
import json
from time import perf_counter_ns

from agentshield.engine import RuntimePolicyEngine
from agentshield.fixtures import SCENARIOS


def percentile(values: list[float], p: float) -> float:
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, int(round((len(ordered) - 1) * p))))
    return ordered[index]


def run(iterations: int) -> dict:
    engine = RuntimePolicyEngine()
    samples_ms: list[float] = []
    for i in range(iterations):
        call = SCENARIOS[i % len(SCENARIOS)]
        start = perf_counter_ns()
        engine.evaluate(call)
        samples_ms.append((perf_counter_ns() - start) / 1_000_000)

    return {
        "iterations": iterations,
        "p50_ms": round(percentile(samples_ms, 0.50), 6),
        "p95_ms": round(percentile(samples_ms, 0.95), 6),
        "p99_ms": round(percentile(samples_ms, 0.99), 6),
        "max_ms": round(max(samples_ms), 6),
        "note": "Local deterministic policy-engine benchmark; not a production latency claim.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--iterations", type=int, default=10_000)
    args = parser.parse_args()
    print(json.dumps(run(args.iterations), indent=2))


if __name__ == "__main__":
    main()

# Security-control measurement

AgentShield's runtime policy answers whether an individual agent action should be allowed, redacted, escalated, or blocked. This measurement layer answers a different question:

> **Does a safeguard reduce meaningful agent risk enough to justify the friction it creates for legitimate work?**

That distinction matters because a control can look strong if judged only by block rate while simultaneously producing unnecessary approvals, failed benign tasks, and operational delay.

## Measurement contract

Each evaluated task records risk, intervention, and observed outcome separately:

```text
event_id
risky
control_action
security_outcome_prevented
task_success
approval_latency_ms
detection_latency_ms
recovery_success
```

The schema deliberately avoids treating `BLOCK` as inherently correct or `ALLOW` as inherently safe. The outcome fields carry the evaluation truth for the synthetic experiment.

## Core metrics

| Metric | Question |
| --- | --- |
| Prevented-risk rate | Of known risky tasks, how often did the safeguard prevent the synthetic adverse outcome? |
| False-positive rate | Of benign tasks, how often were they blocked or forced through approval? |
| Benign task-success rate | Did legitimate work still complete? |
| Approval rate | How much human-review friction did the control create? |
| Approval latency p50 | How long did approval checkpoints delay work? |
| Risky detection latency p50 | How quickly did the control recognize risky synthetic activity? |
| Recovery success | When a recovery path existed, did it complete successfully? |
| Net security utility | Did modeled risk reduction outweigh modeled friction costs? |

## Transparent utility function

The default demonstration score is:

```text
net security utility =
    prevented-risk rate
  - 0.35 × benign false-positive rate
  - 0.15 × approval rate
  - 0.25 × benign task-failure rate
```

These weights are **illustrative scenario assumptions**, not universal security economics. A real deployment should sensitivity-test them with Security, Product, Engineering, and Operations and should report the underlying metrics alongside any aggregate score.

## Synthetic strict-vs-adaptive experiment

`agentshield.measurement_fixtures.synthetic_safeguard_experiment()` provides two deterministic cohorts:

- **strict control** — prevents every risky synthetic outcome but interrupts some benign work;
- **adaptive control** — accepts one residual synthetic risky outcome while eliminating benign block/approval false positives and reducing approval delay.

The example is designed to force a real tradeoff rather than make one policy dominate every metric.

Run the normal AgentShield report after this change to see the control comparison alongside runtime-policy and trajectory-ML evidence.

## Experimentation

`bootstrap_utility_difference()` provides a dependency-free bootstrap interval around candidate-minus-baseline utility for the synthetic fixture. It demonstrates uncertainty-aware comparison rather than relying only on point estimates.

Production experiments need more rigorous design. Depending on rollout mechanics, the analysis may need:

- assignment at user, tenant, agent, or workflow level;
- cluster-aware uncertainty estimates;
- pre-specified guardrails and stopping criteria;
- sequential-testing corrections;
- staged or shadow rollouts when randomized exposure is unsafe;
- observational or causal methods when direct experimentation is not appropriate;
- explicit monitoring of rare high-severity failures even when aggregate utility improves.

## Evaluation boundary

All values in the included experiment are synthetic and deterministic. They validate the measurement and comparison code paths; they do not estimate production attack prevention, false-positive rates, approval latency, or user impact.

The purpose of this layer is methodological: make security effectiveness, control friction, and decision tradeoffs measurable using a shared analytical contract.

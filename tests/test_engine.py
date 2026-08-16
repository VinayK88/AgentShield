import unittest

from agentshield.api import evaluate_payload
from agentshield.engine import RuntimePolicyEngine
from agentshield.fixtures import SCENARIOS
from agentshield.report import build_report


class EngineTests(unittest.TestCase):
    def test_sensitive_read_then_external_write_blocks(self):
        engine = RuntimePolicyEngine()
        self.assertEqual(engine.evaluate(SCENARIOS[0]).decision, "ALLOW")
        self.assertEqual(engine.evaluate(SCENARIOS[1]).decision, "BLOCK")

    def test_destructive_action_requires_approval(self):
        engine = RuntimePolicyEngine()
        self.assertEqual(engine.evaluate(SCENARIOS[2]).decision, "REQUIRE_APPROVAL")

    def test_benign_search_allowed(self):
        engine = RuntimePolicyEngine()
        self.assertEqual(engine.evaluate(SCENARIOS[3]).decision, "ALLOW")

    def test_explicit_sensitive_email_is_redacted(self):
        engine = RuntimePolicyEngine()
        decision = engine.evaluate(SCENARIOS[5])
        self.assertEqual(decision.decision, "ALLOW_WITH_REDACTION")
        self.assertEqual(decision.redactions, ["PII"])

    def test_report_metrics_match_fixture_expectations(self):
        summary = build_report()["summary"]
        self.assertEqual(summary["scenarios"], 6)
        self.assertEqual(summary["exact_policy_matches"], 6)
        self.assertEqual(summary["benign_preserved"], 4)
        self.assertEqual(summary["false_blocks"], 0)
        self.assertEqual(summary["controls_intercepted"], 2)
        self.assertEqual(summary["redacted"], 1)

    def test_api_evaluate_accepts_history(self):
        payload = {
            "history": [SCENARIOS[0].__dict__],
            "call": SCENARIOS[1].__dict__,
        }
        decision = evaluate_payload(payload)
        self.assertEqual(decision["decision"], "BLOCK")
        self.assertIn("sensitive-read → external-write trajectory detected", decision["reasons"])


if __name__ == "__main__":
    unittest.main()

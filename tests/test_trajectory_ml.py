import unittest

from agentshield.engine import DEFAULT_TOOLS
from agentshield.fixtures import SCENARIOS
from agentshield.trajectory_ml import MarkovTrajectoryModel, score_call, score_scenarios, trajectory_report


class TrajectoryMLTests(unittest.TestCase):
    def test_reference_model_is_deterministic(self):
        first = MarkovTrajectoryModel().surprisal(("sensitive_read", "external_write"))
        second = MarkovTrajectoryModel().surprisal(("sensitive_read", "external_write"))
        self.assertAlmostEqual(first, second)

    def test_sensitive_read_to_external_write_is_unusual(self):
        finding = score_call([SCENARIOS[0]], SCENARIOS[1], DEFAULT_TOOLS)
        self.assertGreaterEqual(finding.anomaly_percentile, 90.0)
        self.assertEqual(finding.unusual_transition, "sensitive_read -> external_write")

    def test_scenario_scoring_returns_every_call(self):
        rows = score_scenarios(SCENARIOS, DEFAULT_TOOLS)
        self.assertEqual(len(rows), len(SCENARIOS))
        self.assertTrue(all(0.0 <= row.anomaly_percentile <= 100.0 for row in rows))

    def test_report_keeps_policy_boundary_explicit(self):
        report = trajectory_report(SCENARIOS, DEFAULT_TOOLS)
        self.assertEqual(report["model"], "LaplaceMarkovTrajectoryModel")
        self.assertIn("advisory", report["boundary"].lower())


if __name__ == "__main__":
    unittest.main()

import unittest

from agentshield.measurement import (
    bootstrap_utility_difference,
    compare_controls,
    summarize_control,
)
from agentshield.measurement_fixtures import synthetic_safeguard_experiment


class MeasurementTests(unittest.TestCase):
    def test_strict_control_prevents_all_synthetic_risk(self):
        strict, _ = synthetic_safeguard_experiment()
        summary = summarize_control(strict)
        self.assertEqual(summary["prevented_risk_rate"], 1.0)
        self.assertEqual(summary["false_positive_rate"], 0.25)
        self.assertEqual(summary["benign_task_success_rate"], 0.75)

    def test_adaptive_control_reduces_friction(self):
        strict, adaptive = synthetic_safeguard_experiment()
        comparison = compare_controls(strict, adaptive)
        delta = comparison["delta_candidate_minus_baseline"]
        self.assertLess(delta["prevented_risk_rate"], 0.0)
        self.assertLess(delta["false_positive_rate"], 0.0)
        self.assertGreater(delta["benign_task_success_rate"], 0.0)
        self.assertGreater(delta["net_security_utility"], 0.0)

    def test_bootstrap_is_deterministic_for_fixed_seed(self):
        strict, adaptive = synthetic_safeguard_experiment()
        a = bootstrap_utility_difference(strict, adaptive, iterations=300, seed=9)
        b = bootstrap_utility_difference(strict, adaptive, iterations=300, seed=9)
        self.assertEqual(a, b)
        self.assertGreater(a["observed_difference"], 0.0)
        self.assertLessEqual(a["ci95_low"], a["ci95_high"])

    def test_empty_input_rejected(self):
        with self.assertRaises(ValueError):
            summarize_control([])


if __name__ == "__main__":
    unittest.main()

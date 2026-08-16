import unittest
from agentshield.engine import RuntimePolicyEngine
from agentshield.fixtures import SCENARIOS

class EngineTests(unittest.TestCase):
    def test_sensitive_read_then_external_write_blocks(self):
        e = RuntimePolicyEngine()
        self.assertIn(e.evaluate(SCENARIOS[0]).decision, {"ALLOW", "REQUIRE_APPROVAL"})
        self.assertEqual(e.evaluate(SCENARIOS[1]).decision, "BLOCK")

    def test_destructive_action_requires_control(self):
        e = RuntimePolicyEngine()
        self.assertIn(e.evaluate(SCENARIOS[2]).decision, {"REQUIRE_APPROVAL", "BLOCK"})

    def test_benign_search_allowed(self):
        e = RuntimePolicyEngine()
        self.assertEqual(e.evaluate(SCENARIOS[3]).decision, "ALLOW")

if __name__ == "__main__": unittest.main()

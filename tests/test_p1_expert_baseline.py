"""P1 expert-MR baseline protocol guards.

These tests keep the LLM-simulated expert baseline reproducible without calling
an external gateway: credentials may be supplied through gateway-style aliases,
and every MR verdict must be a strict 2-of-3 majority from exactly three distinct
configured LLM rater models.
"""
import os
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import run_expert_mr_baseline as E  # noqa: E402


class TestGatewayCredentialAliases(unittest.TestCase):
    def test_api_key_and_base_url_aliases_are_accepted(self):
        old_env = os.environ.copy()
        try:
            for name in (*E.API_KEY_ENV_NAMES, *E.BASE_URL_ENV_NAMES):
                os.environ.pop(name, None)
            os.environ["API_KEY"] = "alias-key"
            os.environ["BASE_URL"] = "https://gateway.example/v1"

            api_key, base_url, api_key_env, base_url_env = E._gateway_credentials()

            self.assertEqual(api_key, "alias-key")
            self.assertEqual(base_url, "https://gateway.example/v1")
            self.assertEqual(api_key_env, "API_KEY")
            self.assertEqual(base_url_env, "BASE_URL")
        finally:
            os.environ.clear()
            os.environ.update(old_env)


class TestStrictThreeRaterMajority(unittest.TestCase):
    def test_uses_configured_three_raters_and_ignores_extra_patch_rater(self):
        votes = {
            "claude-opus-4-8": {"overall_verdict": "retain"},
            "MiniMax-M3": {"overall_verdict": "reject"},
            "glm-4": {"overall_verdict": "retain"},
            # A historical rate-limited rater may remain in the audit trail, but
            # the active P1 decision rule is exactly the three configured raters.
            "Kimi-K2-Instruct": {"overall_verdict": "reject"},
        }

        verdict, distribution, active, error = E._strict_three_rater_majority(
            votes, E.RATER_MODELS)

        self.assertEqual(verdict, "retain")
        self.assertEqual(distribution, {"retain": 2, "reject": 1})
        self.assertEqual(active, E.RATER_MODELS)
        self.assertIsNone(error)

    def test_fewer_than_three_successful_raters_is_error(self):
        votes = {
            "claude-opus-4-8": {"overall_verdict": "retain"},
            "MiniMax-M3": {"overall_verdict": "error", "error": "timeout"},
            "glm-4": {"overall_verdict": "retain"},
        }

        verdict, distribution, active, error = E._strict_three_rater_majority(
            votes, E.RATER_MODELS)

        self.assertEqual(verdict, "error")
        self.assertEqual(distribution, {"retain": 2})
        self.assertEqual(active, ["claude-opus-4-8", "glm-4"])
        self.assertIn("expected exactly 3", error)


if __name__ == "__main__":
    unittest.main()

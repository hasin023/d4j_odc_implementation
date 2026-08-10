import os
import unittest
from unittest.mock import patch

from d4j_odc_pipeline.cli import build_parser
from d4j_odc_pipeline.llm import default_model_for_provider


class ModelFlagResolutionTests(unittest.TestCase):
    """Regression: --model must override the provider's env var
    (GEMINI_MODEL/GROQ_MODEL/OPENROUTER_MODEL), not the reverse. Before
    2026-08-10, --model's argparse default was the resolved env-var value
    itself, so an omitted --model was indistinguishable from a user
    explicitly passing that exact value — an explicit --model could never
    win while the provider's env var was set (which it always is), making
    it impossible to run a second model on any strategy."""

    def test_model_flag_omitted_is_none_after_parse(self) -> None:
        with patch.dict(os.environ, {"GEMINI_MODEL": "gemini-3.5-flash-lite"}, clear=False):
            parser = build_parser()
            args = parser.parse_args(["classify", "--context", "x.json"])
            self.assertIsNone(args.model)

    def test_model_flag_explicit_value_survives_parse(self) -> None:
        with patch.dict(os.environ, {"GEMINI_MODEL": "gemini-3.5-flash-lite"}, clear=False):
            parser = build_parser()
            args = parser.parse_args(
                ["classify", "--context", "x.json", "--model", "gemini-3.1-flash-lite"]
            )
            self.assertEqual(args.model, "gemini-3.1-flash-lite")

    @staticmethod
    def _resolve(args):
        """Mirrors main()'s resolution step exactly."""
        if args.model is None:
            args.model = default_model_for_provider(
                args.provider, os.environ.get("DEFAULT_LLM_MODEL", "gemini-3.1-flash-lite")
            )
        return args.model

    def test_resolution_prefers_explicit_model_over_env(self) -> None:
        with patch.dict(os.environ, {"GEMINI_MODEL": "gemini-3.5-flash-lite"}, clear=False):
            parser = build_parser()
            args = parser.parse_args(
                ["classify", "--context", "x.json", "--provider", "gemini", "--model", "gemini-3.1-flash-lite"]
            )
            self.assertEqual(self._resolve(args), "gemini-3.1-flash-lite")

    def test_resolution_falls_back_to_provider_env_when_omitted(self) -> None:
        with patch.dict(os.environ, {"GEMINI_MODEL": "gemini-3.5-flash-lite"}, clear=False):
            parser = build_parser()
            args = parser.parse_args(["classify", "--context", "x.json", "--provider", "gemini"])
            self.assertEqual(self._resolve(args), "gemini-3.5-flash-lite")


if __name__ == "__main__":
    unittest.main()

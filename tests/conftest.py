import pytest

from d4j_odc_pipeline import llm


@pytest.fixture(autouse=True)
def _isolate_llm_logs(tmp_path, monkeypatch):
    """Keep tests from appending fake calls/errors to the real local API logs."""
    monkeypatch.setattr(llm, "_TOKEN_USAGE_LOG", tmp_path / "token_usage_log.jsonl")
    monkeypatch.setattr(llm, "_HTTP_ERROR_LOG", tmp_path / "llm_http_errors.jsonl")

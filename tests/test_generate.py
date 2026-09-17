from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from rag.chunking import Chunk
from rag.generate import MODEL, NO_ANSWER, answer_question, build_messages
from rag.store import SearchResult

RESULTS = [
    SearchResult(Chunk("refunds.md", "Refunds and disputes", "Issuing a refund", "Refunds within 180 days."), 0.82),
    SearchResult(Chunk("payments.md", "Accepting payments", "Processing fees", "0.5% platform fee."), 0.55),
]


def fake_client(text="You can refund within 180 days [1]."):
    client = MagicMock()
    client.messages.create.return_value = SimpleNamespace(
        stop_reason="end_turn",
        content=[SimpleNamespace(type="thinking", thinking=""), SimpleNamespace(type="text", text=text)],
    )
    return client


def test_build_messages_numbers_sources_with_citation_metadata():
    content = build_messages("Can I refund?", RESULTS)[0]["content"]
    assert '<source id="1" doc="refunds.md" section="Refunds and disputes > Issuing a refund">' in content
    assert '<source id="2" doc="payments.md"' in content
    assert content.endswith("Question: Can I refund?")


def test_answer_question_sends_only_confident_sources_to_claude():
    client = fake_client()
    answer = answer_question("Can I refund?", RESULTS, client=client, min_score=0.6)

    assert answer.text == "You can refund within 180 days [1]."
    assert answer.used_model is True
    assert [r.chunk.doc_path for r in answer.sources] == ["refunds.md"]

    kwargs = client.messages.create.call_args.kwargs
    assert kwargs["model"] == MODEL
    assert "only the numbered sources" in kwargs["system"]
    assert "refunds.md" in kwargs["messages"][0]["content"]
    assert "payments.md" not in kwargs["messages"][0]["content"]  # below min_score


def test_weak_retrieval_returns_i_dont_know_without_calling_claude():
    client = fake_client()
    answer = answer_question("Do you have an iPhone app?", RESULTS, client=client, min_score=0.9)
    assert answer.text == NO_ANSWER
    assert answer.used_model is False
    client.messages.create.assert_not_called()


def test_missing_api_key_fails_with_clear_message(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_AUTH_TOKEN", raising=False)
    with pytest.raises(RuntimeError, match="ANTHROPIC_API_KEY is not set"):
        answer_question("Can I refund?", RESULTS, min_score=0.6)

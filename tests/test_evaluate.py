from rag.chunking import Chunk
from rag.evaluate import score_question
from rag.store import SearchResult


def result(doc, text):
    return SearchResult(Chunk(doc, "T", "H", text), score=0.5)


def test_score_question_hit_recall_and_reciprocal_rank():
    results = [result("x.md", "nothing"), result("a.md", "Refunds take 180 days"), result("b.md", "5 seats")]
    evidence = [{"doc": "a.md", "phrase": "180 days"}, {"doc": "c.md", "phrase": "missing"}]
    s = score_question(results, evidence, k=3)
    assert s["hit"] is True
    assert s["hit@1"] is False
    assert s["recall"] == 0.5
    assert s["rr"] == 0.5


def test_phrase_in_wrong_doc_is_not_relevant():
    s = score_question([result("b.md", "180 days")], [{"doc": "a.md", "phrase": "180 days"}], k=5)
    assert s == {"hit@1": False, "hit": False, "recall": 0.0, "rr": 0.0}

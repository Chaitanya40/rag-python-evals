import numpy as np

from rag.chunking import Chunk
from rag.embeddings import normalize
from rag.store import VectorStore


def make_store(tmp_path):
    chunks = [Chunk("a.md", "A", "One", "alpha"), Chunk("b.md", "B", "Two", "beta"), Chunk("c.md", "C", "Three", "gamma")]
    vectors = normalize(np.array([[1, 0, 0], [0, 1, 0], [1, 1, 0]], dtype=np.float32))
    store = VectorStore(tmp_path / "index.sqlite3")
    store.replace_all(chunks, vectors, meta={"model": "test"})
    return store


def test_search_ranks_by_cosine_similarity(tmp_path):
    store = make_store(tmp_path)
    results = store.search(normalize(np.array([1, 0.2, 0], dtype=np.float32)), k=2)
    assert [r.chunk.doc_path for r in results] == ["a.md", "c.md"]
    assert results[0].score > results[1].score
    assert abs(results[0].score - 0.9806) < 1e-3


def test_index_persists_and_replace_all_overwrites(tmp_path):
    make_store(tmp_path)
    reopened = VectorStore(tmp_path / "index.sqlite3")
    assert reopened.meta() == {"model": "test"}
    assert reopened.count() == 3
    assert len(reopened.search(np.array([0, 1, 0], dtype=np.float32), k=10)) == 3

    reopened.replace_all([Chunk("d.md", "D", "Four", "delta")], np.array([[0, 0, 1]], dtype=np.float32), meta={})
    assert [r.chunk.doc_path for r in reopened.search(np.array([0, 0, 1], dtype=np.float32))] == ["d.md"]


def test_empty_store_returns_no_results(tmp_path):
    store = VectorStore(tmp_path / "empty.sqlite3")
    assert store.count() == 0
    assert store.search(np.array([1.0], dtype=np.float32)) == []

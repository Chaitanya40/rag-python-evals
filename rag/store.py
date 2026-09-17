import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from rag.chunking import Chunk


@dataclass
class SearchResult:
    chunk: Chunk
    score: float


class VectorStore:
    """Chunks and embeddings in SQLite; similarity search in numpy."""

    def __init__(self, db_path: Path | str):
        self.conn = sqlite3.connect(db_path)
        self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS chunks (
                id INTEGER PRIMARY KEY,
                doc_path TEXT NOT NULL,
                doc_title TEXT NOT NULL,
                heading TEXT NOT NULL,
                text TEXT NOT NULL,
                embedding BLOB NOT NULL
            );
            CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
            """
        )
        self._matrix: np.ndarray | None = None
        self._chunks: list[Chunk] = []

    def replace_all(self, chunks: list[Chunk], embeddings: np.ndarray, meta: dict) -> None:
        with self.conn:
            self.conn.execute("DELETE FROM chunks")
            self.conn.execute("DELETE FROM meta")
            self.conn.executemany(
                "INSERT INTO chunks (doc_path, doc_title, heading, text, embedding) VALUES (?, ?, ?, ?, ?)",
                [
                    (c.doc_path, c.doc_title, c.heading, c.text, e.astype(np.float32).tobytes())
                    for c, e in zip(chunks, embeddings)
                ],
            )
            self.conn.executemany(
                "INSERT INTO meta (key, value) VALUES (?, ?)",
                [(k, json.dumps(v)) for k, v in meta.items()],
            )
        self._matrix = None  # invalidate the in-memory cache

    def count(self) -> int:
        return self.conn.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]

    def meta(self) -> dict:
        return {k: json.loads(v) for k, v in self.conn.execute("SELECT key, value FROM meta")}

    def _load(self) -> None:
        rows = self.conn.execute(
            "SELECT doc_path, doc_title, heading, text, embedding FROM chunks ORDER BY id"
        ).fetchall()
        self._chunks = [Chunk(r[0], r[1], r[2], r[3]) for r in rows]
        vectors = [np.frombuffer(r[4], dtype=np.float32) for r in rows]
        self._matrix = np.vstack(vectors) if vectors else np.zeros((0, 0), dtype=np.float32)

    def search(self, query_vector: np.ndarray, k: int = 5) -> list[SearchResult]:
        if self._matrix is None:
            self._load()
        if len(self._chunks) == 0:
            return []
        scores = self._matrix @ query_vector  # cosine similarity: vectors are unit length
        top = np.argsort(-scores)[:k]
        return [SearchResult(self._chunks[i], float(scores[i])) for i in top]

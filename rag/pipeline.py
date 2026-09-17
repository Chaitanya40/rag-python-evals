from pathlib import Path

from rag.chunking import chunk_document
from rag.embeddings import Embedder
from rag.loader import load_markdown_docs
from rag.store import SearchResult, VectorStore


def build_index(
    docs_dir: Path,
    store: VectorStore,
    embedder: Embedder,
    max_chars: int = 800,
    overlap_chars: int = 150,
) -> int:
    chunks = []
    for doc in load_markdown_docs(docs_dir):
        chunks.extend(chunk_document(doc, max_chars, overlap_chars))
    embeddings = embedder.embed_passages([c.embedding_text() for c in chunks])
    store.replace_all(
        chunks,
        embeddings,
        meta={"model": embedder.model_name, "max_chars": max_chars, "overlap_chars": overlap_chars},
    )
    return len(chunks)


def retrieve(question: str, store: VectorStore, embedder: Embedder, k: int = 5) -> list[SearchResult]:
    return store.search(embedder.embed_query(question), k=k)

"""Measure retrieval quality against a labelled question set. No API key needed."""

import argparse
import json
import os
import statistics
from dataclasses import dataclass
from pathlib import Path

from rag.chunking import Chunk, chunk_document, chunk_fixed_size
from rag.embeddings import Embedder
from rag.generate import MIN_SCORE
from rag.loader import load_markdown_docs
from rag.store import SearchResult, VectorStore

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.environ.get("RAG_DATA_DIR", PROJECT_ROOT / ".rag-data"))


@dataclass
class Config:
    name: str
    strategy: str  # "headings" or "fixed"
    max_chars: int
    overlap_chars: int
    breadcrumb: bool = True  # prepend doc title and headings before embedding


def is_relevant(chunk: Chunk, evidence: dict) -> bool:
    """A chunk counts as relevant if it comes from the right doc and contains the key phrase."""
    return chunk.doc_path == evidence["doc"] and evidence["phrase"].lower() in chunk.text.lower()


def score_question(results: list[SearchResult], evidence: list[dict], k: int) -> dict:
    top = results[:k]
    found = [any(is_relevant(r.chunk, e) for r in top) for e in evidence]
    first_rank = next(
        (rank for rank, r in enumerate(top, start=1) if any(is_relevant(r.chunk, e) for e in evidence)),
        None,
    )
    return {
        "hit@1": bool(top) and any(is_relevant(top[0].chunk, e) for e in evidence),
        "hit": any(found),  # at least one relevant chunk in the top k
        "recall": sum(found) / len(evidence),  # share of evidence items retrieved
        "rr": 1 / first_rank if first_rank else 0.0,  # reciprocal rank of first relevant chunk
    }


def build_chunks(docs_dir: Path, config: Config) -> list[Chunk]:
    chunks = []
    for doc in load_markdown_docs(docs_dir):
        if config.strategy == "fixed":
            chunks.extend(chunk_fixed_size(doc, config.max_chars, config.overlap_chars))
        else:
            chunks.extend(chunk_document(doc, config.max_chars, config.overlap_chars))
    return chunks


def evaluate(config: Config, questions: list[dict], embedder: Embedder, docs_dir: Path, k: int) -> dict:
    chunks = build_chunks(docs_dir, config)
    store = VectorStore(":memory:")
    texts = [c.embedding_text() if config.breadcrumb else c.text for c in chunks]
    store.replace_all(chunks, embedder.embed_passages(texts), meta={})

    scores, answerable_top, unanswerable_top, misses = [], [], [], []
    for q in questions:
        results = store.search(embedder.embed_query(q["question"]), k=k)
        if not q["evidence"]:  # unanswerable: only record how confident retrieval looked
            unanswerable_top.append(results[0].score)
            continue
        answerable_top.append(results[0].score)
        s = score_question(results, q["evidence"], k)
        scores.append(s)
        if not s["hit"]:
            misses.append(q["question"])

    return {
        "config": config.name,
        "chunks": len(chunks),
        "hit_rate@1": statistics.fmean(s["hit@1"] for s in scores),
        f"hit_rate@{k}": statistics.fmean(s["hit"] for s in scores),
        f"recall@{k}": statistics.fmean(s["recall"] for s in scores),
        "mrr": statistics.fmean(s["rr"] for s in scores),
        "top1_score_answerable": summarize(answerable_top),
        "top1_score_unanswerable": summarize(unanswerable_top),
        f"below_min_score({MIN_SCORE})": f"{sum(x < MIN_SCORE for x in answerable_top)}/{len(answerable_top)} answerable, "
        f"{sum(x < MIN_SCORE for x in unanswerable_top)}/{len(unanswerable_top)} unanswerable",
        "misses": misses,
    }


def summarize(values: list[float]) -> str:
    if not values:
        return "n/a"
    return f"min {min(values):.3f} / median {statistics.median(values):.3f} / max {max(values):.3f}"


EXPERIMENT = [
    Config("fixed-300", "fixed", 300, 60),
    Config("fixed-800", "fixed", 800, 150),
    Config("headings-300", "headings", 300, 60),
    Config("headings-800", "headings", 800, 150),
    Config("headings-800-no-breadcrumb", "headings", 800, 150, breadcrumb=False),
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--questions", type=Path, default=PROJECT_ROOT / "eval" / "questions.jsonl")
    parser.add_argument("--docs", type=Path, default=PROJECT_ROOT / "docs")
    parser.add_argument("-k", type=int, default=5)
    parser.add_argument("--compare", action="store_true", help="run the chunking experiment")
    parser.add_argument("--max-chars", type=int, default=800)
    parser.add_argument("--overlap", type=int, default=150)
    args = parser.parse_args()

    questions = [json.loads(line) for line in args.questions.read_text().splitlines() if line.strip()]
    embedder = Embedder(cache_dir=str(DATA_DIR / "models"))
    configs = EXPERIMENT if args.compare else [
        Config(f"headings-{args.max_chars}", "headings", args.max_chars, args.overlap)
    ]

    answerable = sum(1 for q in questions if q["evidence"])
    print(f"{len(questions)} questions ({answerable} answerable), k={args.k}\n")
    for config in configs:
        report = evaluate(config, questions, embedder, args.docs, args.k)
        misses = report.pop("misses")
        for key, value in report.items():
            print(f"{key:>24}: {value:.3f}" if isinstance(value, float) else f"{key:>24}: {value}")
        for m in misses:
            print(f"{'missed':>24}: {m}")
        print()


if __name__ == "__main__":
    main()

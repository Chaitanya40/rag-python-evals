import argparse
import os
import sys
from pathlib import Path

import anthropic

from rag.embeddings import Embedder
from rag.generate import answer_question
from rag.pipeline import build_index, retrieve
from rag.store import VectorStore

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.environ.get("RAG_DATA_DIR", PROJECT_ROOT / ".rag-data"))


def open_store_and_embedder() -> tuple[VectorStore, Embedder]:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    store = VectorStore(DATA_DIR / "index.sqlite3")
    embedder = Embedder(cache_dir=str(DATA_DIR / "models"))
    return store, embedder


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="rag")
    sub = parser.add_subparsers(dest="command", required=True)

    ingest = sub.add_parser("ingest", help="chunk, embed and store the docs")
    ingest.add_argument("--docs", type=Path, default=PROJECT_ROOT / "docs")
    ingest.add_argument("--max-chars", type=int, default=800)
    ingest.add_argument("--overlap", type=int, default=150)

    for name in ("search", "ask"):
        p = sub.add_parser(name)
        p.add_argument("question")
        p.add_argument("-k", type=int, default=5)

    args = parser.parse_args(argv)
    store, embedder = open_store_and_embedder()

    if args.command == "ingest":
        n = build_index(args.docs, store, embedder, args.max_chars, args.overlap)
        print(f"Indexed {n} chunks into {DATA_DIR / 'index.sqlite3'}")
        return 0

    if store.count() == 0:
        print("error: the index is empty. Run `python -m rag.cli ingest` first.", file=sys.stderr)
        return 1

    results = retrieve(args.question, store, embedder, k=args.k)
    if args.command == "search":
        for r in results:
            print(f"{r.score:.3f}  {r.chunk.doc_path}  [{r.chunk.heading}]")
        return 0

    try:
        answer = answer_question(args.question, results)
    except RuntimeError as err:
        print(f"error: {err}", file=sys.stderr)
        return 2
    except anthropic.AuthenticationError:
        print("error: the API rejected your key (401). Check ANTHROPIC_API_KEY.", file=sys.stderr)
        return 2
    except anthropic.RateLimitError:
        # The SDK already retried with backoff (max_retries defaults to 2).
        print("error: rate limited (429) after retries. Wait and try again.", file=sys.stderr)
        return 3
    except anthropic.APIConnectionError:
        print("error: could not reach the Anthropic API. Check your network.", file=sys.stderr)
        return 3
    print(answer.text)
    if answer.sources:
        print("\nSources:")
        for n, r in enumerate(answer.sources, start=1):
            print(f"[{n}] {r.chunk.doc_path} > {r.chunk.heading} (score {r.score:.2f})")
    return 0


if __name__ == "__main__":
    sys.exit(main())

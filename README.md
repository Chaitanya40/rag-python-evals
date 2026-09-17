# Kestrel RAG: a small, measurable retrieval-augmented generation pipeline

Companion code for the tutorial "How to Add RAG to a Python App: Chunking, Retrieval, and Evaluation".

The pipeline answers questions about Kestrel, a fictional invoicing app, using the help-center articles in `docs/`:

1. Load markdown files (`rag/loader.py`)
2. Split them into heading-aware chunks with overlap (`rag/chunking.py`)
3. Embed chunks locally with fastembed and `BAAI/bge-small-en-v1.5` (`rag/embeddings.py`)
4. Store chunks and vectors in SQLite and search with numpy cosine similarity (`rag/store.py`)
5. Build a grounded prompt with numbered sources and generate a cited answer with Claude (`rag/generate.py`)
6. Measure retrieval with hit rate, recall@k and MRR on a labeled question set (`rag/evaluate.py`, `eval/questions.jsonl`)

Ingestion, search, evaluation and the tests run without an API key. Only `ask` calls the Claude API.

## Requirements

- Python 3.12 or newer (pinned in `.python-version`)
- [uv](https://docs.astral.sh/uv/)
- An Anthropic API key for the `ask` command

## Setup

```bash
uv sync
```

The first command that embeds text downloads the embedding model (about 65 MB) into `.rag-data/models/`. The SQLite index is written to `.rag-data/index.sqlite3`. Set `RAG_DATA_DIR` to store both somewhere else. `.rag-data/` is gitignored.

## Usage

```bash
# Chunk, embed and index docs/
uv run python -m rag.cli ingest

# Inspect retrieval only (no API key needed)
uv run python -m rag.cli search "Can I get my Stripe fee back after a refund?"

# Retrieve and generate a cited answer with Claude
export ANTHROPIC_API_KEY=...
uv run python -m rag.cli ask "Can I get my Stripe fee back after a refund?"
```

`ingest` accepts `--docs`, `--max-chars` and `--overlap`. `search` and `ask` accept `-k`. The Claude model defaults to `claude-opus-5`; override it with `RAG_CLAUDE_MODEL`.

If the best retrieved chunk scores below `MIN_SCORE` (0.60, in `rag/generate.py`), `ask` answers "I don't know" without calling the API.

## Evaluation

```bash
# Evaluate the default configuration (heading-aware, 800 chars, 150 overlap)
uv run python -m rag.evaluate

# Compare fixed-size and heading-aware chunking at different sizes
uv run python -m rag.evaluate --compare

# Try your own settings
uv run python -m rag.evaluate --max-chars 400 --overlap 80 -k 3
```

Each line of `eval/questions.jsonl` is a question plus the evidence that answers it: a document path and a short phrase that must appear in a retrieved chunk. Questions with an empty `evidence` list are unanswerable from the docs; the script reports their top similarity scores so you can calibrate `MIN_SCORE`.

### Results on the sample corpus

`--compare` (k=5), all measured on the 38 questions in `eval/questions.jsonl`:

```
config                      chunks  hit@1  hit@5  MRR
fixed-300                   79      0.750  0.875  0.794
fixed-800                   32      0.688  0.969  0.812
headings-300                85      0.812  0.938  0.870
headings-800                66      0.875  0.938  0.901
headings-800-no-breadcrumb  66      0.812  0.938  0.875
```

`--max-chars 1500 --overlap 250` gives the same results as 800, because no section in the sample docs is longer than 800 characters.

Top-k sweep for the default configuration (`-k 1`, `-k 3`, `-k 5`, `-k 10`):

```
k=1   hit_rate 0.875  recall 0.859  mrr 0.875
k=3   hit_rate 0.938  recall 0.938  mrr 0.901
k=5   hit_rate 0.938  recall 0.938  mrr 0.901
k=10  hit_rate 1.000  recall 1.000  mrr 0.908
```

## Brute-force search speed

`VectorStore.search` scores every chunk with one numpy matrix multiplication and an `argsort`. Measured with random 384-dimensional float32 vectors on an Apple M5 laptop (numpy 2.5.3, mean of 10 queries):

```
chunks      latency   matrix memory
10,000      0.6 ms    15 MB
100,000     7.2 ms    154 MB
1,000,000   93.5 ms   1,536 MB
```

To reproduce:

```bash
uv run python -c "
import numpy as np, time
for n in (10_000, 100_000, 1_000_000):
    m = np.random.rand(n, 384).astype(np.float32); q = np.random.rand(384).astype(np.float32)
    t = time.perf_counter()
    for _ in range(10):
        s = m @ q; top = np.argsort(-s)[:5]
    print(n, f'{(time.perf_counter() - t) / 10 * 1000:.1f} ms', f'{m.nbytes / 1e6:.0f} MB')
"
```

## Troubleshooting

- `uv sync` reports that Python 3.9 is incompatible: run `uv python install 3.12`. The `.python-version` file selects it.
- `error: ANTHROPIC_API_KEY is not set`: export the key in the shell that runs `ask`. Retrieval and evaluation don't need it.
- `error: the API rejected your key (401)`: the key is invalid or revoked.
- `error: rate limited (429) after retries`: the SDK already retried twice with backoff. Wait, or lower your request rate.
- `error: the index is empty`: run `ingest` first, with the same `RAG_DATA_DIR`.
- "You are sending unauthenticated requests to the HF Hub" on the first run is a harmless warning from the model download. Set `HF_TOKEN` if you hit download rate limits.

## Tests

```bash
uv run pytest
```

The generation tests use a mocked Anthropic client, so they don't need a key or network access.

## Project layout

```
docs/               sample help-center articles (fictional product)
eval/questions.jsonl labeled questions for retrieval evaluation
rag/                pipeline source
tests/              unit tests
```

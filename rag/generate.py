import os
from dataclasses import dataclass

import anthropic

from rag.store import SearchResult

MODEL = os.environ.get("RAG_CLAUDE_MODEL", "claude-opus-5")

# Below this cosine similarity, we don't trust retrieval enough to ask the model.
# Calibrate it with `python -m rag.evaluate`, which prints score distributions.
MIN_SCORE = 0.60

NO_ANSWER = "I don't know. I couldn't find this in the help center."

SYSTEM_PROMPT = """You answer questions from customers of Kestrel, an invoicing app.
Answer using only the numbered sources provided in the user's message.
Cite every claim with the source number in square brackets, like [1] or [2][3].
If the sources don't contain the answer, reply exactly: "I don't know. I couldn't find this in the help center."
Do not use outside knowledge about Kestrel or guess at product behavior."""


@dataclass
class Answer:
    text: str
    sources: list[SearchResult]
    used_model: bool


def format_sources(results: list[SearchResult]) -> str:
    blocks = []
    for n, r in enumerate(results, start=1):
        c = r.chunk
        blocks.append(
            f'<source id="{n}" doc="{c.doc_path}" section="{c.doc_title} > {c.heading}">\n'
            f"{c.text}\n</source>"
        )
    return "\n\n".join(blocks)


def build_messages(question: str, results: list[SearchResult]) -> list[dict]:
    content = f"<sources>\n{format_sources(results)}\n</sources>\n\nQuestion: {question}"
    return [{"role": "user", "content": content}]


def has_credentials() -> bool:
    return bool(os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN"))


def answer_question(
    question: str,
    results: list[SearchResult],
    client: anthropic.Anthropic | None = None,
    min_score: float = MIN_SCORE,
) -> Answer:
    # The "I don't know" path: weak retrieval never reaches the model.
    confident = [r for r in results if r.score >= min_score]
    if not confident:
        return Answer(NO_ANSWER, sources=[], used_model=False)

    if client is None:
        if not has_credentials():
            raise RuntimeError(
                "ANTHROPIC_API_KEY is not set. Retrieval works without a key, "
                "but generating an answer needs one: export ANTHROPIC_API_KEY=..."
            )
        client = anthropic.Anthropic()

    response = client.messages.create(
        model=MODEL,
        max_tokens=16000,
        system=SYSTEM_PROMPT,
        messages=build_messages(question, confident),
    )
    # The response can also contain thinking blocks; keep only the text.
    text = "".join(block.text for block in response.content if block.type == "text")
    return Answer(text.strip(), confident, used_model=True)

from rag.chunking import Chunk, chunk_document, pack_units, split_sections, split_units
from rag.loader import Document

DOC = """# Billing

Intro paragraph.

## Refunds

Refunds take 5 days.

### Partial refunds

Enter an amount.

```bash
# not a heading
curl example
```
"""


def test_split_sections_tracks_heading_path_and_ignores_code_fences():
    sections = split_sections(DOC)
    assert [path for path, _ in sections] == [
        ["Billing"],
        ["Billing", "Refunds"],
        ["Billing", "Refunds", "Partial refunds"],
    ]
    assert "# not a heading" in sections[2][1]


def test_chunk_document_uses_breadcrumb_headings():
    chunks = chunk_document(Document("billing.md", "Billing", DOC), max_chars=800)
    assert [c.heading for c in chunks] == ["Billing", "Refunds", "Refunds > Partial refunds"]
    assert chunks[1].embedding_text().startswith("Billing\nRefunds\n\n")


def test_long_paragraphs_are_split_by_sentence():
    text = "First sentence here. Second sentence here. Third sentence here."
    units = split_units(text, max_chars=25)
    assert units == ["First sentence here.", "Second sentence here.", "Third sentence here."]


def test_pack_units_respects_max_chars_and_overlaps():
    units = ["a" * 40, "b" * 40, "c" * 40, "d" * 40]
    chunks = pack_units(units, max_chars=90, overlap_chars=45)
    assert all(len(c) <= 90 for c in chunks)
    assert chunks[0].endswith("b" * 40) and chunks[1].startswith("b" * 40)  # overlap carried


def test_every_word_survives_chunking():
    body = "\n\n".join(f"Paragraph {i} " + "word " * 30 for i in range(10))
    doc = Document("x.md", "X", f"# X\n\n## Section\n\n{body}")
    joined = " ".join(c.text for c in chunk_document(doc, max_chars=300, overlap_chars=60))
    for i in range(10):
        assert f"Paragraph {i}" in joined


def test_embedding_text_skips_empty_heading():
    assert Chunk("x.md", "X", "", "body").embedding_text() == "X\n\nbody"

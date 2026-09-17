import re
from dataclasses import dataclass

from rag.loader import Document

HEADING = re.compile(r"^(#{1,6})\s+(.*)$")


@dataclass
class Chunk:
    doc_path: str
    doc_title: str
    heading: str  # breadcrumb, e.g. "Recurring invoices > Automatic charging"
    text: str

    def embedding_text(self) -> str:
        """The text to embed: document title and headings give the chunk context."""
        header = "\n".join(part for part in (self.doc_title, self.heading) if part)
        return f"{header}\n\n{self.text}"


def split_sections(markdown: str) -> list[tuple[list[str], str]]:
    """Split markdown into (heading path, body) pairs, ignoring '#' inside code fences."""
    sections = []
    path: list[str] = []
    body: list[str] = []
    in_fence = False
    for line in markdown.splitlines():
        if line.strip().startswith("```"):
            in_fence = not in_fence
        match = None if in_fence else HEADING.match(line)
        if match:
            sections.append((list(path), "\n".join(body).strip()))
            level = len(match.group(1))
            path = path[: level - 1] + [match.group(2).strip()]
            body = []
        else:
            body.append(line)
    sections.append((list(path), "\n".join(body).strip()))
    return [(p, b) for p, b in sections if b]


def split_units(text: str, max_chars: int) -> list[str]:
    """Break text into paragraphs, falling back to sentences, then words, for long ones."""
    units = []
    for para in re.split(r"\n\s*\n", text):
        para = para.strip()
        if len(para) <= max_chars:
            units.append(para)
            continue
        for sentence in re.split(r"(?<=[.!?])\s+", para):
            while len(sentence) > max_chars:
                cut = sentence.rfind(" ", 0, max_chars)
                cut = cut if cut > 0 else max_chars
                units.append(sentence[:cut])
                sentence = sentence[cut:].strip()
            units.append(sentence)
    return [u for u in units if u]


def pack_units(units: list[str], max_chars: int, overlap_chars: int) -> list[str]:
    """Greedily pack units into chunks, repeating trailing units as overlap."""
    chunks: list[str] = []
    current: list[str] = []
    for unit in units:
        if current and len("\n\n".join(current + [unit])) > max_chars:
            chunks.append("\n\n".join(current))
            # Carry the last few units forward so context spans the boundary.
            carried: list[str] = []
            for previous in reversed(current):
                if len("\n\n".join([previous] + carried)) > overlap_chars:
                    break
                carried.insert(0, previous)
            while carried and len("\n\n".join(carried + [unit])) > max_chars:
                carried.pop(0)
            current = carried
        current.append(unit)
    if current:
        chunks.append("\n\n".join(current))
    return chunks


def chunk_document(doc: Document, max_chars: int = 800, overlap_chars: int = 150) -> list[Chunk]:
    chunks = []
    for path, body in split_sections(doc.text):
        heading = " > ".join(path[1:]) or doc.title  # path[0] is the H1 title
        for text in pack_units(split_units(body, max_chars), max_chars, overlap_chars):
            chunks.append(Chunk(doc.path, doc.title, heading, text))
    return chunks


def chunk_fixed_size(doc: Document, size: int = 800, overlap: int = 150) -> list[Chunk]:
    """Naive baseline: fixed character windows that ignore document structure."""
    step = size - overlap
    return [
        Chunk(doc.path, doc.title, "", doc.text[start : start + size])
        for start in range(0, max(len(doc.text) - overlap, 1), step)
    ]

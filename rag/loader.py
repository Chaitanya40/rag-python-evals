from dataclasses import dataclass
from pathlib import Path


@dataclass
class Document:
    path: str  # relative path, used as a stable ID and in citations
    title: str
    text: str


def load_markdown_docs(root: Path) -> list[Document]:
    """Load every .md file under root, using the first H1 as the title."""
    docs = []
    for file in sorted(root.rglob("*.md")):
        text = file.read_text(encoding="utf-8")
        title = file.stem.replace("-", " ").title()
        for line in text.splitlines():
            if line.startswith("# "):
                title = line[2:].strip()
                break
        docs.append(Document(path=file.relative_to(root).as_posix(), title=title, text=text))
    return docs

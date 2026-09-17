import numpy as np
from fastembed import TextEmbedding

DEFAULT_MODEL = "BAAI/bge-small-en-v1.5"  # 384 dimensions, ~65 MB quantized ONNX download


class Embedder:
    def __init__(self, model_name: str = DEFAULT_MODEL, cache_dir: str | None = None):
        self.model_name = model_name
        self._model = TextEmbedding(model_name, cache_dir=cache_dir)

    def embed_passages(self, texts: list[str]) -> np.ndarray:
        return normalize(np.array(list(self._model.passage_embed(texts)), dtype=np.float32))

    def embed_query(self, text: str) -> np.ndarray:
        return normalize(np.array(list(self._model.query_embed(text)), dtype=np.float32))[0]


def normalize(vectors: np.ndarray) -> np.ndarray:
    """Scale rows to unit length so a dot product equals cosine similarity."""
    norms = np.linalg.norm(vectors, axis=-1, keepdims=True)
    return vectors / np.clip(norms, 1e-12, None)

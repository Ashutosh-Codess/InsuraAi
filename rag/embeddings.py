"""
Embedding generation. The doc says "open-weight embeddings integration"
without naming a specific model, so I went with sentence-transformers'
all-MiniLM-L6-v2 - small, runs on CPU fine, no API key needed, which fits
the "no third-party data transmission" angle the rest of the stack is
going for. Swap MODEL_NAME if you want a different one.
"""
from sentence_transformers import SentenceTransformer

MODEL_NAME = "all-MiniLM-L6-v2"

_model = None


def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def embed_texts(texts: list[str]) -> list[list[float]]:
    model = get_model()
    return model.encode(texts, convert_to_numpy=True).tolist()


def embed_text(text: str) -> list[float]:
    return embed_texts([text])[0]

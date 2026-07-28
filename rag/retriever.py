"""
Retrieves the most relevant chunks from a Chroma collection for a given
query. This is what rag_tool.py (in agents/tools/) calls when an agent
needs grounded context.
"""
from rag.embeddings import embed_text
from vector_db.client import get_or_create_collection


def retrieve(collection_name: str, query: str, top_k: int = 5) -> list[dict]:
    collection = get_or_create_collection(collection_name)
    query_embedding = embed_text(query)

    results = collection.query(query_embeddings=[query_embedding], n_results=top_k)

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    return [
        {"text": doc, "metadata": meta, "distance": dist}
        for doc, meta, dist in zip(documents, metadatas, distances)
    ]

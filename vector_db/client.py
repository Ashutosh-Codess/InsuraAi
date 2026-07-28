"""
Wraps the Chroma client. Went with Chroma over Pinecone (the doc listed
both) since it's self-hosted, which matches the doc's own reasoning for
using open-weight local LLMs in the first place - no reason to send
policy/medical embeddings to a third-party cloud service if the whole
point was avoiding third-party data transmission.
"""
import chromadb

_client = None


def get_client() -> chromadb.ClientAPI:
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path="./chroma_data")
    return _client


def get_or_create_collection(name: str):
    return get_client().get_or_create_collection(name=name)

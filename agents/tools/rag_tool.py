"""
Lets an agent pull relevant chunks from a vector collection. Wraps
rag/retriever.py so agents get a plain text answer they can drop into
their reasoning.
"""
from crewai.tools import tool

from rag.retriever import retrieve
from vector_db.collections import ALL_COLLECTIONS


@tool("knowledge_base_search")
def knowledge_base_search(collection_name: str, query: str) -> str:
    """Searches one of the knowledge base collections (policy_terms,
    medical_rules, repair_estimates, regulatory_rules) and returns the
    top matching chunks."""
    if collection_name not in ALL_COLLECTIONS:
        return f"Unknown collection '{collection_name}'. Valid options: {ALL_COLLECTIONS}"

    results = retrieve(collection_name, query)
    if not results:
        return "No relevant information found in the knowledge base for this query."

    return "\n\n".join(f"[{r['metadata'].get('source_file', 'unknown')}] {r['text']}" for r in results)

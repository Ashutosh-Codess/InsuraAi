"""
Loads text documents into the four vector collections. Run manually or on
a schedule whenever policy wording, medical rules, or regulatory text
changes:

    python -m vector_db.indexer
"""
import os
import uuid

from rag.chunking import chunk_text
from rag.embeddings import embed_texts
from vector_db.client import get_or_create_collection
from vector_db.collections import MEDICAL_RULES, POLICY_TERMS, REGULATORY_RULES, REPAIR_ESTIMATES

# maps each collection to the folder it reads .txt source files from
SOURCE_DIRS = {
    POLICY_TERMS: "data/raw/policy_terms",
    MEDICAL_RULES: "data/raw/medical_rules",
    REPAIR_ESTIMATES: "data/raw/repair_estimates",
    REGULATORY_RULES: "data/raw/regulatory_rules",
}


def index_collection(collection_name: str, source_dir: str):
    if not os.path.isdir(source_dir):
        print(f"[indexer] {source_dir} doesn't exist yet, skipping {collection_name}")
        return

    collection = get_or_create_collection(collection_name)

    for filename in os.listdir(source_dir):
        if not filename.endswith(".txt"):
            continue

        path = os.path.join(source_dir, filename)
        with open(path, "r") as f:
            text = f.read()

        chunks = chunk_text(text)
        if not chunks:
            continue

        embeddings = embed_texts(chunks)
        ids = [str(uuid.uuid4()) for _ in chunks]
        metadatas = [{"source_file": filename} for _ in chunks]

        collection.add(ids=ids, embeddings=embeddings, documents=chunks, metadatas=metadatas)
        print(f"[indexer] indexed {len(chunks)} chunks from {filename} into {collection_name}")


def run():
    for collection_name, source_dir in SOURCE_DIRS.items():
        index_collection(collection_name, source_dir)


if __name__ == "__main__":
    run()

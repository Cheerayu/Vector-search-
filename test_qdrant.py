from qdrant_client import QdrantClient
from qdrant_client.http import models as qm

client = QdrantClient(url="http://localhost:6333")  # REST on 6333

# 1) Service health/info (simple endpoint hit)
info = client.get_locks()  # service API: lightweight status call
print("Service locks:", info)

# 2) High-level helpers (auto-embeddings with FastEmbed)
collection = "doclib_smoke"
docs = [
    "Qdrant is a vector database.",
    "FastEmbed generates embeddings quickly.",
    "WSL2 backend runs Docker Desktop efficiently."
]
ids = client.add(collection_name=collection, documents=docs)  # will create collection as needed
print("Inserted IDs:", ids)

res = client.query(collection_name=collection, query_text="vector DB", limit=3)
print("Query results:", res)

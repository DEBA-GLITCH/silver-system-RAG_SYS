import json
from embeddings.embedder import SimpleEmbedder
from embeddings.embedding_store import EmbeddingStore
from embeddings.vector_index import VectorIndex

# Load chunks
with open("data/chunks.json", "r") as f:
    chunks = json.load(f)

embedder = SimpleEmbedder(dim=256)
store = EmbeddingStore("data/embeddings.json")

# Build embeddings
for chunk in chunks:
    vec = embedder.embed(chunk["chunk_text"])
    store.add(
        chunk_id=chunk["chunk_id"],
        vector=vec,
        model_name=embedder.model_name
    )

# Query test
query = "food delivery startup failed logistics"
query_vec = embedder.embed(query)

index = VectorIndex(store.all())
results = index.search(query_vec, top_k=3)

print("Top matches:")
for cid, score in results:
    print(cid, score)

print("\nFull results")




from embeddings.embedder import SimpleEmbedder
from retrieval.retriever import Retriever

embedder = SimpleEmbedder(dim=256)

retriever = Retriever(
    embedding_store_path="data/embeddings.json",
    embedder=embedder,
    min_similarity=0.35,
    max_chunks=5
)

query = "why did my food delivery startup fail"

result = retriever.retrieve(query)

print(result)

from typing import List, Dict
from embeddings.embedder import SimpleEmbedder
from embeddings.embedding_store import EmbeddingStore
from embeddings.vector_index import VectorIndex


class Retriever:
    """
    Evidence exposure controller.
    Decides which chunks are allowed to influence reasoning.
    """

    def __init__(
        self,
        embedding_store_path: str,
        embedder: SimpleEmbedder,
        min_similarity: float = 0.35,
        max_chunks: int = 5
    ):
        self.embedder = embedder
        self.min_similarity = min_similarity
        self.max_chunks = max_chunks

        # Load embeddings (derived, disposable)
        self.store = EmbeddingStore(embedding_store_path)

        # Build similarity index
        self.index = VectorIndex(self.store.all())

    def retrieve(self, query_text: str) -> Dict:
        """
        Retrieve admissible evidence for a query.
        """
        # 1️⃣ Embed query (normalized)
        query_vector = self.embedder.embed(query_text)

        # 2️⃣ Similarity search (candidate generation)
        candidates = self.index.search(
            query_vector,
            top_k=self.max_chunks * 2  # fetch more, filter later
        )

        # 3️⃣ Similarity threshold (admissibility gate)
        admissible = [
            {
                "chunk_id": chunk_id,
                "similarity": score
            }
            for chunk_id, score in candidates
            if score >= self.min_similarity
        ]

        # 4️⃣ Sort by similarity (strongest evidence first)
        admissible.sort(key=lambda x: x["similarity"], reverse=True)

        # 5️⃣ Top-k truncation (context budget)
        admissible = admissible[: self.max_chunks]

        # 6️⃣ Retrieval status decision
        if len(admissible) == 0:
            status = "EMPTY"
        elif len(admissible) <= 2:
            status = "LOW_CONFIDENCE"
        else:
            status = "SUCCESS"

        # Attach rank
        for i, item in enumerate(admissible):
            item["rank"] = i + 1

        return {
            "status": status,
            "results": admissible
        }

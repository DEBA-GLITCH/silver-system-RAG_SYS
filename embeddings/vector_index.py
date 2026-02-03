from typing import Dict, List, Tuple


class VectorIndex:
    """
    Simple in-memory cosine similarity index.
    """

    def __init__(self, embeddings: Dict[str, Dict]):
        self.vectors = {
            cid: data["embedding"]
            for cid, data in embeddings.items()
        }

    def _dot(self, a: List[float], b: List[float]) -> float:
        return sum(x * y for x, y in zip(a, b))

    def search(
        self,
        query_vector: List[float],
        top_k: int = 5
    ) -> List[Tuple[str, float]]:

        scores = []

        for chunk_id, vector in self.vectors.items():
            score = self._dot(query_vector, vector)
            scores.append((chunk_id, score))

        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]

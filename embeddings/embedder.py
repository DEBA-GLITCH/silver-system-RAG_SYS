import math
import re
from typing import List
import hashlib


class SimpleEmbedder:
    """
    Deterministic, local text embedder.
    Converts text into a fixed-size normalized vector.
    """

    def __init__(self, dim: int = 256):
        self.dim = dim
        self.model_name = f"hash-bow-{dim}"

    def _tokenize(self, text: str) -> List[str]:
        # lowercase + simple word split
        return re.findall(r"\b\w+\b", text.lower())

    def embed(self, text: str) -> List[float]:
        vector = [0.0] * self.dim
        tokens = self._tokenize(text)

        for token in tokens:
            # stable hash → index
            h = int(hashlib.sha256(token.encode()).hexdigest(), 16)
            idx = h % self.dim
            vector[idx] += 1.0

        return self._normalize(vector)

    def _normalize(self, vector: List[float]) -> List[float]:
        norm = math.sqrt(sum(x * x for x in vector))
        if norm == 0:
            return vector
        return [x / norm for x in vector]

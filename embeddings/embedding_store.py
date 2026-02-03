import json
import os
from datetime import datetime
from typing import Dict, List


class EmbeddingStore:
    """
    Disk-backed store for embeddings.
    Safe to delete and rebuild.
    """

    def __init__(self, path: str):
        self.path = path
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        self.embeddings: Dict[str, Dict] = {}
        self._load()

    def _load(self):
        if os.path.exists(self.path):
            with open(self.path, "r") as f:
                self.embeddings = json.load(f)
        else:
            self._persist()

    def _persist(self):
        with open(self.path, "w") as f:
            json.dump(self.embeddings, f, indent=2)

    def add(
        self,
        chunk_id: str,
        vector: List[float],
        model_name: str,
        normalized: bool = True
    ):
        self.embeddings[chunk_id] = {
            "chunk_id": chunk_id,
            "embedding": vector,
            "embedding_model": model_name,
            "normalized": normalized,
            "created_at": datetime.utcnow().isoformat()
        }
        self._persist()

    def all(self) -> Dict[str, Dict]:
        return self.embeddings
    

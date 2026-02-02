import json
import os


class VectorStore:
    """
    Placeholder vector index.
    Embeddings will be added in Phase-2.
    """

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.vectors = {}
        self._load()

    def _load(self):
        if os.path.exists(self.filepath):
            with open(self.filepath, "r") as f:
                self.vectors = json.load(f)
        else:
            self._persist()

    def _persist(self):
        with open(self.filepath, "w") as f:
            json.dump(self.vectors, f)

    def add(self, memory_id: str, embedding):
        """
        Associates an embedding with a memory_id.
        """
        self.vectors[memory_id] = embedding
        self._persist()

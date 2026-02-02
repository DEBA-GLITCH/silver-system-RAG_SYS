import json
import os
import uuid
from datetime import datetime
from typing import List, Dict


class MetadataStore:
    """
    Disk-backed, append-only memory store.
    This is the system's source of truth.
    """

    def __init__(self, filepath: str):
        self.filepath = filepath

        # Ensure parent directory exists BEFORE any file operation
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)

        # In-memory working copy of all memories
        self.memories: List[Dict] = []

        # Load existing memories from disk
        self._load()

    def _load(self):
        """
        Loads memory log from disk into RAM.
        If file does not exist, initializes an empty log safely.
        """
        if not os.path.exists(self.filepath):
            self._atomic_persist()

        with open(self.filepath, "r") as f:
            self.memories = json.load(f)

    def _atomic_persist(self):
        """
        Writes memory to disk atomically.
        Prevents partial writes and corruption on crashes.
        """
        temp_path = self.filepath + ".tmp"

        with open(temp_path, "w") as f:
            json.dump(self.memories, f, indent=2)

        # Atomic filesystem-level replacement
        os.replace(temp_path, self.filepath)

    def add_memory(self, text: str, source: str, mem_type: str) -> Dict:
        """
        Appends a new memory entry.
        Existing memory is NEVER modified.
        """
        memory = {
            "memory_id": str(uuid.uuid4()),
            "text": text,
            "source": source,
            "type": mem_type,
            "timestamp": datetime.utcnow().isoformat(),
            "embedding_ref": None
        }

        # Append-only behavior
        self.memories.append(memory)

        # Persist immediately to minimize crash window
        self._atomic_persist()

        return memory

    def all_memories(self) -> List[Dict]:
        """
        Returns the full memory log.
        """
        return self.memories






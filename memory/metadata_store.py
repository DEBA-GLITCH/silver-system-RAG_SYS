import json
import os
import uuid
from datetime import datetime
from typing import List, Dict, Optional


class MetadataStore:
    """
    Disk-backed source-of-truth store.

    Responsibilities:
    - Store raw memories (append-only, immutable truth)
    - Store derived chunks (rebuildable meaning units)
    - Provide safe read access for downstream phases
    """

    def __init__(self, filepath: str):
        self.filepath = filepath

        # Ensure directory exists
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)

        # In-memory state
        self.memories: List[Dict] = []
        self.chunks: Dict[str, Dict] = {}

        # Load from disk (backward compatible)
        self._load()

    # -------------------------------------------------
    # Disk I/O (with backward compatibility)
    # -------------------------------------------------

    def _load(self):
        """
        Load metadata from disk.

        Supports:
        - Phase-1 schema: List[Memory]
        - Phase-2+ schema: { memories: [...], chunks: {...} }
        """
        if not os.path.exists(self.filepath):
            self._atomic_persist()
            return

        with open(self.filepath, "r") as f:
            data = json.load(f)

        # Phase-1 legacy format (list of memories only)
        if isinstance(data, list):
            self.memories = data
            self.chunks = {}

        # Phase-2+ format (dict with memories + chunks)
        elif isinstance(data, dict):
            self.memories = data.get("memories", [])
            self.chunks = data.get("chunks", {})

        else:
            raise ValueError("Unsupported metadata schema format")

    def _atomic_persist(self):
        """
        Atomically write metadata to disk.
        Prevents corruption on crash or partial write.
        """
        temp_path = self.filepath + ".tmp"

        with open(temp_path, "w") as f:
            json.dump(
                {
                    "memories": self.memories,
                    "chunks": self.chunks,
                },
                f,
                indent=2
            )

        os.replace(temp_path, self.filepath)

    # -------------------------------------------------
    # Memory API (Phase-1)
    # -------------------------------------------------

    def add_memory(self, text: str, source: str, mem_type: str) -> Dict:
        """
        Append a new raw memory.
        Existing memories are never modified.
        """
        memory = {
            "memory_id": str(uuid.uuid4()),
            "text": text,
            "source": source,
            "type": mem_type,
            "timestamp": datetime.utcnow().isoformat(),
        }

        self.memories.append(memory)
        self._atomic_persist()
        return memory

    def all_memories(self) -> List[Dict]:
        """
        Return all stored raw memories.
        """
        return self.memories

    # -------------------------------------------------
    # Chunk API (Phase-2 → Phase-4)
    # -------------------------------------------------

    def add_chunk(self, chunk: Dict):
        """
        Store a derived chunk.

        Chunk must include:
        - chunk_id
        - chunk_text
        - memory_id (recommended)
        """
        self.chunks[chunk["chunk_id"]] = chunk
        self._atomic_persist()

    def get_chunk(self, chunk_id: str) -> Optional[Dict]:
        """
        Resolve chunk_id → chunk data.
        Used by AnswerGenerator.
        """
        return self.chunks.get(chunk_id)

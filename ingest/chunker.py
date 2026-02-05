import json
import os
import uuid
from datetime import datetime
from typing import List, Dict


class Chunker:
    """
    Deterministic chunking engine.
    Transforms memory text into semantically coherent chunks.
    """

    def __init__(self, memory_path: str, chunk_path: str):
        self.memory_path = memory_path
        self.chunk_path = chunk_path

        # Ensure output directory exists
        os.makedirs(os.path.dirname(self.chunk_path), exist_ok=True)

    def load_memories(self) -> List[Dict]:
        """
        Load source-of-truth memories ONLY.
        """
        with open(self.memory_path, "r") as f:
            data = json.load(f)

        # 🔒 CRITICAL FIX: metadata.json is a dict, not a list
        if isinstance(data, dict):
            return data.get("memories", [])

        return data  # fallback (older formats)

    def save_chunks(self, chunks: List[Dict]):
        """
        Persist derived chunks (disposable).
        """
        with open(self.chunk_path, "w") as f:
            json.dump(chunks, f, indent=2)

    def chunk_text(self, text: str) -> List[str]:
        """
        Chunk text based on paragraph boundaries first.
        Paragraphs are semantic hints, not hard rules.
        """
        raw_paragraphs = [
            p.strip() for p in text.split("\n\n") if p.strip()
        ]

        chunks = []
        buffer = ""

        for paragraph in raw_paragraphs:
            if not buffer:
                buffer = paragraph
                continue

            # Merge small dependent paragraphs
            if len(paragraph.split()) < 40:
                buffer += " " + paragraph
            else:
                chunks.append(buffer)
                buffer = paragraph

        if buffer:
            chunks.append(buffer)

        return chunks

    def build_chunks(self) -> List[Dict]:
        """
        Core transformation:
        Memory -> Chunks
        """
        memories = self.load_memories()
        all_chunks = []

        for memory in memories:
            memory_id = memory["memory_id"]
            source = memory["source"]
            created_at = datetime.utcnow().isoformat()

            text_chunks = self.chunk_text(memory["text"])

            for idx, chunk_text in enumerate(text_chunks):
                chunk = {
                    "chunk_id": str(uuid.uuid4()),
                    "memory_id": memory_id,
                    "chunk_index": idx,
                    "chunk_text": chunk_text,
                    "source": source,
                    "created_at": created_at,
                }
                all_chunks.append(chunk)

        return all_chunks

    def run(self):
        """
        End-to-end chunking pipeline.
        """
        chunks = self.build_chunks()
        self.save_chunks(chunks)
        print(f"Chunking complete. Generated {len(chunks)} chunks.")

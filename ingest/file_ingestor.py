import os
from pypdf import PdfReader

from memory.metadata_store import MetadataStore
from embeddings.embedder import SimpleEmbedder
from embeddings.embedding_store import EmbeddingStore
from ingest.chunker import Chunker


class FileIngestor:
    """
    Deterministic file ingestion pipeline.

    File → raw memory → batch chunker → embeddings
    """

    def __init__(
        self,
        metadata_path: str,
        embedding_store_path: str,
        embedder: SimpleEmbedder,
        chunker: Chunker,
    ):
        self.metadata_store = MetadataStore(metadata_path)
        self.embedding_store = EmbeddingStore(embedding_store_path)
        self.embedder = embedder
        self.chunker = chunker

    # -------------------------------------------------
    # Public API
    # -------------------------------------------------

    def ingest(self, filepath: str):
        if not os.path.exists(filepath):
            raise FileNotFoundError(filepath)

        # 1️⃣ Read file into raw text
        text = self._read_file(filepath)

        # 2️⃣ Store raw memory (append-only truth)
        self.metadata_store.add_memory(
            text=text,
            source=filepath,
            mem_type="file",
        )

        # 3️⃣ Clear old chunks (derived data)
        self.chunker.save_chunks([])

        # 4️⃣ Rebuild ALL chunks deterministically
        chunks = self.chunker.build_chunks()
        self.chunker.save_chunks(chunks)

        
        # 4️⃣ Persist chunks + embeddings (immediate-write store)
        for chunk in chunks:
            self.metadata_store.add_chunk(chunk)

            vector = self.embedder.embed(chunk["chunk_text"])
            self.embedding_store.add(
                chunk_id=chunk["chunk_id"],
                vector=vector,
                model_name=self.embedder.model_name,
            )

    # -------------------------------------------------
    # File readers
    # -------------------------------------------------

    def _read_file(self, filepath: str) -> str:
        ext = os.path.splitext(filepath)[1].lower()

        if ext in [".txt", ".md"]:
            return self._read_text_file(filepath)

        if ext == ".pdf":
            return self._read_pdf(filepath)

        raise ValueError(f"Unsupported file type: {ext}")

    def _read_text_file(self, filepath: str) -> str:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()

    def _read_pdf(self, filepath: str) -> str:
        reader = PdfReader(filepath)
        pages = []

        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages.append(text)

        return "\n".join(pages)

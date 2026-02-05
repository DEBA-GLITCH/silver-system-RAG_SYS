from ingest.file_ingestor import FileIngestor
from ingest.chunker import Chunker
from embeddings.embedder import SimpleEmbedder

# Paths used consistently across the system
METADATA_PATH = "data/metadata.json"
EMBEDDINGS_PATH = "data/embeddings.json"
CHUNKS_PATH = "data/chunks.json"

chunker = Chunker(
    memory_path=METADATA_PATH,
    chunk_path=CHUNKS_PATH,
)

ingestor = FileIngestor(
    metadata_path=METADATA_PATH,
    embedding_store_path=EMBEDDINGS_PATH,
    embedder=SimpleEmbedder(dim=256),
    chunker=chunker,
)

ingestor.ingest("data/sample_document.txt")
print("Ingestion complete.")

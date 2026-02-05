import sys
import os

from ingest.file_ingestor import FileIngestor
from ingest.chunker import Chunker
from embeddings.embedder import SimpleEmbedder
from retrieval.retriever import Retriever
from llm.answer_generator import AnswerGenerator


# -----------------------------
# CONFIG
# -----------------------------

DATA_DIR = "data"

METADATA_PATH = os.path.join(DATA_DIR, "metadata.json")
CHUNK_PATH = os.path.join(DATA_DIR, "chunks.json")
EMBEDDING_PATH = os.path.join(DATA_DIR, "embeddings.json")


# -----------------------------
# Command handlers
# -----------------------------

def handle_ingest(filepath: str):
    embedder = SimpleEmbedder()

    chunker = Chunker(
        memory_path=METADATA_PATH,
        chunk_path=CHUNK_PATH,
    )

    ingestor = FileIngestor(
        metadata_path=METADATA_PATH,
        embedding_store_path=EMBEDDING_PATH,
        embedder=embedder,
        chunker=chunker,
    )

    ingestor.ingest(filepath)
    print("Ingestion complete.")


def handle_ask(query: str):
    embedder = SimpleEmbedder()

    retriever = Retriever(
        embedding_store_path=EMBEDDING_PATH,
        embedder=embedder,  # 🔒 REQUIRED
    )

    retrieval_result = retriever.retrieve(query)

    generator = AnswerGenerator(
        metadata_store_path=METADATA_PATH
    )

    answer = generator.generate(
        query_text=query,
        retrieval_status=retrieval_result["status"],
        retrieved_chunks=retrieval_result["results"],
    )

    print("\nAnswer:")
    print(answer["answer_text"])
    print(f"\nConfidence: {answer['confidence']}")


def handle_chat():
    print("Entering chat mode. Type 'exit' to quit.\n")

    embedder = SimpleEmbedder()

    retriever = Retriever(
        embedding_store_path=EMBEDDING_PATH,
        embedder=embedder,  # 🔒 REQUIRED
    )

    generator = AnswerGenerator(
        metadata_store_path=METADATA_PATH
    )

    while True:
        query = input("> ").strip()
        if query.lower() in {"exit", "quit"}:
            break

        retrieval_result = retriever.retrieve(query)

        answer = generator.generate(
            query_text=query,
            retrieval_status=retrieval_result["status"],
            retrieved_chunks=retrieval_result["results"],
        )

        print(answer["answer_text"])
        print(f"[confidence: {answer['confidence']}]\n")


# -----------------------------
# Entry point
# -----------------------------

def main():
    if len(sys.argv) < 2:
        print(
            "Usage:\n"
            "  python main.py ingest <file_path>\n"
            "  python main.py ask <question>\n"
            "  python main.py chat"
        )
        return

    command = sys.argv[1]

    if command == "ingest":
        if len(sys.argv) != 3:
            print("Usage: python main.py ingest <file_path>")
            return
        handle_ingest(sys.argv[2])

    elif command == "ask":
        if len(sys.argv) < 3:
            print("Usage: python main.py ask <question>")
            return
        query = " ".join(sys.argv[2:])
        handle_ask(query)

    elif command == "chat":
        handle_chat()

    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()

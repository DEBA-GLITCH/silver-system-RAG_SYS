from embeddings.embedder import SimpleEmbedder
from retrieval.retriever import Retriever
from llm.answer_generator import AnswerGenerator
from dotenv import load_dotenv
import os

embedder = SimpleEmbedder(dim=256)

retriever = Retriever(
    embedding_store_path="data/embeddings.json",
    embedder=embedder,
    min_similarity=0.35,
    max_chunks=5
)

generator = AnswerGenerator(
    metadata_store_path="data/metadata.json"
)

query = "why did my food delivery startup fail"

retrieval_result = retriever.retrieve(query)

answer = generator.generate(
    query_text=query,
    retrieval_status=retrieval_result["status"],
    retrieved_chunks=retrieval_result["results"]
)

print(answer)

from typing import Dict, List
from memory.metadata_store import MetadataStore


class AnswerGenerator:
    """
    Knowledge-grounded answer generator.
    Language is strictly constrained by retrieved evidence.
    """

    def __init__(self, metadata_store_path: str):
        # Source of truth for chunk text
        self.metadata_store = MetadataStore(metadata_store_path)

    def generate(
        self,
        query_text: str,
        retrieval_status: str,
        retrieved_chunks: List[Dict]
    ) -> Dict:
        """
        Generate an answer based strictly on retrieval outcome.
        """

        if retrieval_status == "EMPTY":
            return self._handle_empty(query_text)

        # Resolve chunk_id → chunk_text
        chunk_texts = self._resolve_chunks(retrieved_chunks)

        if retrieval_status == "LOW_CONFIDENCE":
            return self._handle_low_confidence(query_text, chunk_texts)

        if retrieval_status == "SUCCESS":
            return self._handle_success(query_text, chunk_texts)

        raise ValueError(f"Unknown retrieval status: {retrieval_status}")

    # -----------------------------
    # Retrieval status handlers
    # -----------------------------

    def _handle_empty(self, query_text: str) -> Dict:
        return {
            "answer_text": (
                "I don’t have any stored knowledge that can answer this question yet."
            ),
            "confidence": "EMPTY",
            "grounded_chunk_ids": []
        }

    def _handle_low_confidence(
        self,
        query_text: str,
        chunk_texts: List[Dict]
    ) -> Dict:
        answer = self._mock_llm_answer(
            query_text=query_text,
            chunk_texts=chunk_texts,
            cautious=True
        )

        return {
            "answer_text": answer,
            "confidence": "LOW",
            "grounded_chunk_ids": [c["chunk_id"] for c in chunk_texts]
        }

    def _handle_success(
        self,
        query_text: str,
        chunk_texts: List[Dict]
    ) -> Dict:
        answer = self._mock_llm_answer(
            query_text=query_text,
            chunk_texts=chunk_texts,
            cautious=False
        )

        return {
            "answer_text": answer,
            "confidence": "HIGH",
            "grounded_chunk_ids": [c["chunk_id"] for c in chunk_texts]
        }

    # -----------------------------
    # Helpers
    # -----------------------------

    def _resolve_chunks(self, retrieved_chunks: List[Dict]) -> List[Dict]:
        """
        Resolve chunk_id to actual chunk text from metadata store.
        """
        resolved = []

        for item in retrieved_chunks:
            chunk = self.metadata_store.get_chunk(item["chunk_id"])
            if chunk:
                resolved.append({
                    "chunk_id": item["chunk_id"],
                    "chunk_text": chunk["chunk_text"]
                })

        return resolved

    def _mock_llm_answer(
        self,
        query_text: str,
        chunk_texts: List[Dict],
        cautious: bool
    ) -> str:
        """
        Deterministic placeholder for LLM reasoning.
        ONLY uses provided chunk text.
        """

        evidence = " ".join(c["chunk_text"] for c in chunk_texts)

        if cautious:
            return (
                "Based on limited stored information, it appears that: "
                f"{evidence}"
            )

        return f"Based on your stored knowledge: {evidence}"




import os
from typing import Dict, List
from memory.metadata_store import MetadataStore
from dotenv import load_dotenv
load_dotenv()


try:
    from groq import Groq
except ImportError:
    Groq = None


class AnswerGenerator:
    """
    Knowledge-grounded answer generator.
    Uses Groq as a language renderer under strict constraints.
    """

    def __init__(self, metadata_store_path: str, use_groq: bool = True):
        self.metadata_store = MetadataStore(metadata_store_path)

        self.use_groq = use_groq and Groq is not None
        self.groq_client = None

        if self.use_groq:
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise RuntimeError("GROQ_API_KEY not set in environment")

            self.groq_client = Groq(api_key=api_key)

    # -------------------------------------------------
    # Public API
    # -------------------------------------------------

    def generate(
        self,
        query_text: str,
        retrieval_status: str,
        retrieved_chunks: List[Dict]
    ) -> Dict:

        if retrieval_status == "EMPTY":
            return self._handle_empty()

        chunk_texts = self._resolve_chunks(retrieved_chunks)

        if retrieval_status == "LOW_CONFIDENCE":
            answer = self._answer_with_llm(
                query_text, chunk_texts, cautious=True
            )
            confidence = "LOW"

        elif retrieval_status == "SUCCESS":
            answer = self._answer_with_llm(
                query_text, chunk_texts, cautious=False
            )
            confidence = "HIGH"

        else:
            raise ValueError(f"Unknown retrieval status: {retrieval_status}")

        return {
            "answer_text": answer,
            "confidence": confidence,
            "grounded_chunk_ids": [c["chunk_id"] for c in chunk_texts],
        }

    # -------------------------------------------------
    # Retrieval handling
    # -------------------------------------------------

    def _handle_empty(self) -> Dict:
        return {
            "answer_text": (
                "I don’t have any stored knowledge that can answer this question yet."
            ),
            "confidence": "EMPTY",
            "grounded_chunk_ids": [],
        }

    def _resolve_chunks(self, retrieved_chunks: List[Dict]) -> List[Dict]:
        resolved = []

        for item in retrieved_chunks:
            chunk = self.metadata_store.get_chunk(item["chunk_id"])
            if chunk:
                resolved.append(
                    {
                        "chunk_id": item["chunk_id"],
                        "chunk_text": chunk["chunk_text"],
                    }
                )

        return resolved

    # -------------------------------------------------
    # LLM Interface (Groq or Mock)
    # -------------------------------------------------

    def _answer_with_llm(
        self,
        query_text: str,
        chunk_texts: List[Dict],
        cautious: bool,
    ) -> str:

        if not chunk_texts:
            # Absolute grounding rule: no evidence, no facts
            return (
                "Based on limited stored information, I cannot provide a reliable answer."
            )

        context = "\n".join(
            f"- {c['chunk_text']}" for c in chunk_texts
        )

        system_prompt = (
            "You are a knowledge-grounded assistant.\n"
            "You may ONLY answer using the provided context.\n"
            "Do NOT use general world knowledge.\n"
            "If the context is insufficient, say so explicitly.\n"
        )

        if cautious:
            system_prompt += (
                "The evidence is limited. Use cautious, hedged language.\n"
            )

        user_prompt = (
            f"Question:\n{query_text}\n\n"
            f"Context:\n{context}"
        )

        if self.use_groq:
            return self._groq_completion(system_prompt, user_prompt)

        # Fallback deterministic behavior
        return self._mock_llm_answer(context, cautious)

    def _groq_completion(self, system_prompt: str, user_prompt: str) -> str:
        response = self.groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.1,
            max_tokens=512,
        )

        return response.choices[0].message.content.strip()

    # -------------------------------------------------
    # Deterministic fallback (for testing)
    # -------------------------------------------------

    def _mock_llm_answer(self, context: str, cautious: bool) -> str:
        if cautious:
            return (
                "Based on limited stored information, it appears that: "
                + context
            )
        return "Based on your stored knowledge: " + context

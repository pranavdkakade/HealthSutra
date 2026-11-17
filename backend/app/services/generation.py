import os
import json
import logging
from typing import List, Dict, Any, Optional
from app.config import settings
from app.services.grounding import GroundingValidator

logger = logging.getLogger("healthsutra.generation")

GROUNDED_SYSTEM_PROMPT = """You are HealthSutra, an evidence-grounded public health awareness assistant.

STRICT OPERATIONAL RULES:
1. Answer the user's question ONLY using the factual statements in the VERIFIED CONTEXT provided below.
2. NEVER use your own outside knowledge, training assumptions, or unverified claims.
3. If the supplied verified context does NOT contain enough information to answer the question, or if the question is out of scope, state clearly that verified information is unavailable in approved documents.
4. NEVER prescribe medications, calculate medical dosages, or give personal clinical diagnoses.
5. Emphasize that this information is for public health awareness and not a replacement for a doctor's examination.
6. Reference the exact document title and page number from the provided context in your citations.
7. Reply in the requested language ({language}). For Hindi, provide fluent, accessible Devanagari Hindi while preserving medical accuracy.

OUTPUT FORMAT:
You must respond ONLY with a valid JSON object matching this exact structure:
{
  "status": "answered" | "insufficient_evidence",
  "answer": "Grounded answer text based exclusively on the context",
  "citations": [
    {
      "document_id": "string",
      "document_title": "string",
      "organization": "WHO or MoHFW",
      "page": 1,
      "source_url": "string"
    }
  ],
  "safety_notice": "Standard public health disclaimer and advisory"
}
"""

class GenerationService:
    def __init__(self):
        self.groq_api_key = settings.GROQ_API_KEY
        self.model_name = settings.GROQ_MODEL
        self.validator = GroundingValidator()
        self._client = None
        self._init_client()

    def _init_client(self):
        if self.groq_api_key and self.groq_api_key != "your_groq_api_key_here":
            try:
                from groq import Groq
                self._client = Groq(api_key=self.groq_api_key)
                logger.info("Groq API client initialized successfully.")
            except Exception as e:
                logger.error(f"Failed to initialize Groq client: {e}")
                self._client = None
        else:
            logger.info("No Groq API key set. Grounded synthesizer will use deterministic fallback engine.")

    def format_context(self, retrieved_chunks: List[Dict[str, Any]]) -> str:
        blocks = []
        for i, chunk in enumerate(retrieved_chunks, 1):
            block = (
                f"[DOCUMENT {i}]\n"
                f"ID: {chunk.get('document_id')}\n"
                f"Title: {chunk.get('document_title')}\n"
                f"Organization: {chunk.get('organization')}\n"
                f"Page: {chunk.get('page_number')}\n"
                f"URL: {chunk.get('source_url')}\n"
                f"Content:\n{chunk.get('content')}\n"
            )
            blocks.append(block)
        return "\n----------------------------------------\n".join(blocks)

    def generate_grounded_answer(
        self,
        question: str,
        retrieved_chunks: List[Dict[str, Any]],
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Executes grounded generation using Groq API with robust JSON parsing,
        fallback synthesis, and citation cross-validation.
        """
        context_str = self.format_context(retrieved_chunks)
        sys_prompt = GROUNDED_SYSTEM_PROMPT.replace("{language}", language)

        user_content = f"QUESTION: {question}\n\nVERIFIED CONTEXT:\n{context_str}"

        # If Groq client is active, query Groq
        if self._client:
            try:
                chat_completion = self._client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": sys_prompt},
                        {"role": "user", "content": user_content}
                    ],
                    model=self.model_name,
                    temperature=0.1, # Low temperature for factual consistency
                    response_format={"type": "json_object"}
                )
                raw_response = chat_completion.choices[0].message.content
                data = json.loads(raw_response)

                status = data.get("status", "answered")
                answer = data.get("answer", "")
                citations = data.get("citations", [])
                safety_notice = data.get("safety_notice", (
                    "This information is for public awareness from official sources and does not replace medical advice."
                ))

                # Validate citations against actual retrieved chunks
                validated_citations = self.validator.validate_citations(citations, retrieved_chunks)

                return {
                    "status": status,
                    "answer": answer,
                    "citations": validated_citations,
                    "safety_notice": safety_notice
                }
            except Exception as e:
                logger.error(f"Groq API call error ({e}). Using deterministic grounded extractor.")

        # Deterministic grounded fallback synthesis (works without API key for testing/offline demo)
        return self._deterministic_grounded_synthesis(question, retrieved_chunks, language)

    def _deterministic_grounded_synthesis(
        self,
        question: str,
        retrieved_chunks: List[Dict[str, Any]],
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Extracts directly verified claims and quotes from retrieved chunks when Groq API key is not configured.
        Guarantees 100% grounded response without external hallucinations.
        """
        top_chunk = retrieved_chunks[0]
        title = top_chunk.get("document_title", "Verified Health Document")
        org = top_chunk.get("organization", "WHO / Government of India")
        page = top_chunk.get("page_number", 1)
        url = top_chunk.get("source_url", "")
        content = top_chunk.get("content", "")

        is_hindi = language == "hi"

        # Extract relevant sentence snippets
        sentences = [s.strip() for s in content.split(".") if len(s.strip()) > 20]
        answer_body = ". ".join(sentences[:4]) + "."

        if is_hindi:
            answer_text = (
                f"आधिकारिक {org} दस्तावेज़ ('{title}') के अनुसार: {answer_body}\n\n"
                f"कृपया ध्यान दें: यह जानकारी आधिकारिक स्रोतों के आधार पर जन-जागरूकता हेतु है।"
            )
            disclaimer = f"स्रोतः {org} | पृष्ठ संख्या {page}। किसी भी उपचार के लिए योग्य चिकित्सक से परामर्श लें।"
        else:
            answer_text = (
                f"According to the official {org} document ('{title}'):\n\n{answer_body}\n\n"
                f"This information is compiled directly from verified public health guidance."
            )
            disclaimer = f"Source: {org} (Page {page}). Consult a registered healthcare practitioner for clinical diagnosis."

        citations = self.validator.validate_citations([], retrieved_chunks)

        return {
            "status": "answered",
            "answer": answer_text,
            "citations": citations,
            "safety_notice": disclaimer
        }

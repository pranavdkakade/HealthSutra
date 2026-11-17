import re
import logging
from typing import List, Dict, Any, Tuple
from app.config import settings

logger = logging.getLogger("healthsutra.grounding")

class GroundingValidator:
    # Real-time and hyper-local patterns not present in national/WHO guidance documents
    LOCAL_REALTIME_PATTERNS = [
        r"\b(in my village|in rampur|in kanpur|in sector|district hospital|yesterday|this week|right now|current count|admitted yesterday)\b",
        r"\b(मेरे गाँव में|कल रात|इस हफ्ते|वर्तमान आंकड़े|कितने मरीज मिले)\b"
    ]

    # Unverified folklore and speculative home remedy claims
    FOLKLORE_PATTERNS = [
        r"\b(papaya leaf|raw garlic|homeopathic drops|cow milk substitute|boil.*leaves|cure.*within 24 hours)\b",
        r"\b(पपीते का पत्ता|गिलोय|नीम के पत्ते|२४ घंटे में ठीक|गाय का दूध)\b"
    ]

    def __init__(self, threshold: float = None):
        self.threshold = threshold or settings.RELEVANCE_THRESHOLD

    def evaluate_evidence(self, query: str, retrieved_chunks: List[Dict[str, Any]]) -> Tuple[bool, str, float]:
        """
        Determines whether retrieved chunks provide sufficient verified evidence.
        Returns: (has_evidence, reason, best_score)
        """
        if not retrieved_chunks:
            return False, "No documents matched the query.", 0.0

        lowered_q = query.lower()

        # 1. Hyper-local & real-time surveillance check
        for pattern in self.LOCAL_REALTIME_PATTERNS:
            if re.search(pattern, lowered_q, re.IGNORECASE):
                logger.info(f"Refusing query due to real-time/hyper-local request: '{query}'")
                return False, "Local, real-time epidemiological case data is not available in approved public health guidance documents.", 0.0

        # 2. Score threshold check
        best_score = float(retrieved_chunks[0].get("score", 0.0))
        logger.info(f"Top retrieval similarity score: {best_score:.4f} (Threshold: {self.threshold})")

        if best_score < self.threshold:
            return False, f"Relevance score {best_score:.4f} is below verified threshold {self.threshold}.", best_score

        # 3. Folklore / unverified claim verification in context
        combined_text = " ".join([c.get("content", "") for c in retrieved_chunks[:3]]).lower()
        for pattern in self.FOLKLORE_PATTERNS:
            if re.search(pattern, lowered_q, re.IGNORECASE):
                # Verify if the specific claim entity actually exists in official verified text
                matched_term = re.search(pattern, lowered_q, re.IGNORECASE).group(0)
                if matched_term not in combined_text:
                    logger.info(f"Refusing unverified alternative health claim '{matched_term}' not present in verified source text.")
                    return False, f"The claim '{matched_term}' is not supported or documented in verified WHO/MoHFW public health documents.", best_score

        # 4. Check content richness
        if len(combined_text.strip()) < 40:
            return False, "Matched passages are too sparse to formulate an evidence-based answer.", best_score

        return True, "Sufficient verified evidence found.", best_score

    def validate_citations(
        self,
        citations: List[Dict[str, Any]],
        retrieved_chunks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Ensures every citation in the LLM response maps to an actual retrieved chunk.
        Prevents LLMs from inventing document titles, pages, or URLs.
        """
        retrieved_titles = {c.get("document_title", "").strip().lower(): c for c in retrieved_chunks}
        retrieved_ids = {c.get("document_id", "").strip().lower(): c for c in retrieved_chunks}

        validated = []
        for cit in citations:
            doc_id = str(cit.get("document_id", "")).strip().lower()
            doc_title = str(cit.get("document_title", "")).strip().lower()

            matching_chunk = None
            if doc_id in retrieved_ids:
                matching_chunk = retrieved_ids[doc_id]
            elif doc_title in retrieved_titles:
                matching_chunk = retrieved_titles[doc_title]
            else:
                # Fuzzy fallback matching
                for r_title, chunk in retrieved_titles.items():
                    if doc_title and (doc_title in r_title or r_title in doc_title):
                        matching_chunk = chunk
                        break

            if matching_chunk:
                validated.append({
                    "document_id": matching_chunk.get("document_id"),
                    "document_title": matching_chunk.get("document_title"),
                    "organization": matching_chunk.get("organization"),
                    "page": cit.get("page") or matching_chunk.get("page_number", 1),
                    "source_url": matching_chunk.get("source_url"),
                    "confidence_score": matching_chunk.get("score", 0.85),
                    "snippet": matching_chunk.get("content", "")[:180] + "..."
                })
            else:
                logger.warning(f"Stripping ungrounded citation hallucinated by LLM: {cit}")

        # If LLM didn't return valid citations but retrieved chunks are verified, populate from top chunk
        if not validated and retrieved_chunks:
            top_c = retrieved_chunks[0]
            validated.append({
                "document_id": top_c.get("document_id"),
                "document_title": top_c.get("document_title"),
                "organization": top_c.get("organization"),
                "page": top_c.get("page_number", 1),
                "source_url": top_c.get("source_url"),
                "confidence_score": top_c.get("score", 0.85),
                "snippet": top_c.get("content", "")[:180] + "..."
            })

        return validated

import pytest
from app.services.grounding import GroundingValidator

def test_evidence_evaluation_low_score():
    validator = GroundingValidator(threshold=0.55)
    retrieved = [
        {"score": 0.32, "content": "Some completely unrelated information about economy."}
    ]
    has_evidence, reason, score = validator.evaluate_evidence("What are symptoms of dengue?", retrieved)
    assert has_evidence is False
    assert score == 0.32
    assert "below verified threshold" in reason

def test_evidence_evaluation_sufficient():
    validator = GroundingValidator(threshold=0.55)
    retrieved = [
        {"score": 0.82, "content": "Dengue causes high fever, severe headache, eye pain and joint pain. Most patients recover."}
    ]
    has_evidence, reason, score = validator.evaluate_evidence("What are symptoms of dengue?", retrieved)
    assert has_evidence is True
    assert score == 0.82

def test_citation_validation_strips_hallucinations():
    validator = GroundingValidator()
    retrieved_chunks = [
        {
            "document_id": "WHO_DENGUE_001",
            "document_title": "Dengue and severe dengue",
            "organization": "WHO",
            "page_number": 2,
            "source_url": "https://www.who.int/dengue",
            "score": 0.89,
            "content": "Dengue symptoms include high fever and headache."
        }
    ]

    # LLM hallucinated a non-existent document
    hallucinated_citations = [
        {
            "document_id": "FAKE_DOC_999",
            "document_title": "Invented Miracle Cures 2026",
            "organization": "Unknown",
            "page": 99,
            "source_url": "https://fake.com"
        }
    ]

    validated = validator.validate_citations(hallucinated_citations, retrieved_chunks)
    assert len(validated) == 1
    # Should fall back to the actual verified retrieved chunk
    assert validated[0]["document_id"] == "WHO_DENGUE_001"
    assert validated[0]["document_title"] == "Dengue and severe dengue"

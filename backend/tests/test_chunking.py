import pytest
from app.services.chunking import TextChunker

def test_clean_text():
    chunker = TextChunker()
    raw = "Header 1\n\n\n\n12\n\nSome paragraph text here.    Multiple   spaces."
    cleaned = chunker.clean_text(raw)
    assert "12" not in cleaned.split("\n")
    assert "  " not in cleaned
    assert "Some paragraph text here." in cleaned

def test_chunk_page_content():
    chunker = TextChunker(chunk_size=50, overlap=10)
    raw_text = (
        "Dengue is a mosquito-borne viral disease that has rapidly spread in all regions of WHO in recent years. "
        "Dengue virus is transmitted by female mosquitoes mainly of the species Aedes aegypti and, to a lesser extent, Ae. albopictus. "
        "These mosquitoes are also vectors of chikungunya, yellow fever and Zika viruses. "
        "Dengue is widespread throughout the tropics, with local variations in risk influenced by rainfall, temperature, relative humidity and rapid unplanned urbanization."
    )
    chunks = chunker.chunk_page_content(
        document_id="TEST_01",
        document_title="Test Document",
        organization="WHO",
        page_number=1,
        raw_text=raw_text,
        source_url="https://example.com"
    )

    assert len(chunks) > 0
    assert chunks[0]["document_id"] == "TEST_01"
    assert chunks[0]["document_title"] == "Test Document"
    assert chunks[0]["organization"] == "WHO"
    assert chunks[0]["page_number"] == 1
    assert "chunk_id" in chunks[0]
    assert "content_hash" in chunks[0]

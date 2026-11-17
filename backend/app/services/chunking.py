import hashlib
import re
from typing import List, Dict, Any

class TextChunker:
    def __init__(self, chunk_size: int = 600, overlap: int = 100):
        """
        Token-aware recursive chunker for medical documents.
        chunk_size: approximate tokens (1 token ≈ 4 characters)
        overlap: token overlap
        """
        self.chunk_size_chars = chunk_size * 4
        self.overlap_chars = overlap * 4

    def clean_text(self, text: str) -> str:
        """Remove redundant whitespace, headers/footers, and line-breaks."""
        text = re.sub(r"\r\n|\r", "\n", text)
        # Remove standalone page numbers
        text = re.sub(r"^\s*\d+\s*$", "", text, flags=re.MULTILINE)
        # Collapse multiple spaces
        text = re.sub(r"[ \t]+", " ", text)
        # Collapse excessive newlines
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    def chunk_page_content(
        self,
        document_id: str,
        document_title: str,
        organization: str,
        page_number: int,
        raw_text: str,
        source_url: str
    ) -> List[Dict[str, Any]]:
        """
        Divides page text into overlapping paragraph-friendly chunks with rich metadata.
        """
        cleaned = self.clean_text(raw_text)
        if not cleaned or len(cleaned) < 50:
            return []

        # Split on paragraph boundaries first
        paragraphs = cleaned.split("\n\n")
        chunks = []
        current_chunk = ""
        chunk_idx = 0

        for p in paragraphs:
            p = p.strip()
            if not p:
                continue

            if len(current_chunk) + len(p) + 2 <= self.chunk_size_chars:
                current_chunk = f"{current_chunk}\n\n{p}".strip()
            else:
                if current_chunk:
                    chunk_id = f"{document_id}_p{page_number}_c{chunk_idx}"
                    content_hash = hashlib.sha256(current_chunk.encode()).hexdigest()[:16]
                    chunks.append({
                        "chunk_id": chunk_id,
                        "document_id": document_id,
                        "document_title": document_title,
                        "organization": organization,
                        "page_number": page_number,
                        "content": current_chunk,
                        "token_count": len(current_chunk) // 4,
                        "content_hash": content_hash,
                        "source_url": source_url
                    })
                    chunk_idx += 1
                    # Overlap with tail of previous chunk
                    current_chunk = current_chunk[-self.overlap_chars:] + "\n\n" + p
                else:
                    current_chunk = p

        if current_chunk and len(current_chunk.strip()) > 30:
            chunk_id = f"{document_id}_p{page_number}_c{chunk_idx}"
            content_hash = hashlib.sha256(current_chunk.encode()).hexdigest()[:16]
            chunks.append({
                "chunk_id": chunk_id,
                "document_id": document_id,
                "document_title": document_title,
                "organization": organization,
                "page_number": page_number,
                "content": current_chunk.strip(),
                "token_count": len(current_chunk) // 4,
                "content_hash": content_hash,
                "source_url": source_url
            })

        return chunks

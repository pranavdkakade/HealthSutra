import os
import shutil
import logging
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from typing import Optional
from app.config import settings
from app.schemas.api_schemas import DocumentListResponse, DocumentMetadata
from app.services.ingestion import IngestionManager

logger = logging.getLogger("healthsutra.api.documents")
router = APIRouter()
ingestion_manager = IngestionManager()

@router.get("/documents", response_model=DocumentListResponse)
def get_documents():
    docs = ingestion_manager.list_documents()
    formatted = [
        DocumentMetadata(
            id=d["id"],
            title=d["title"],
            organization=d["organization"],
            document_type=d["document_type"],
            disease_category=d.get("disease_category", "General"),
            publication_date=d.get("publication_date", ""),
            source_url=d["source_url"],
            file_path=d.get("file_path", ""),
            verified=d.get("verified", True),
            language=d.get("language", "en"),
            chunks_count=d.get("chunks_count", 0)
        )
        for d in docs
    ]
    return DocumentListResponse(total_documents=len(formatted), documents=formatted)

@router.get("/documents/{doc_id}", response_model=DocumentMetadata)
def get_document_by_id(doc_id: str):
    doc = ingestion_manager.registry.get(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail=f"Document '{doc_id}' not found in registry.")
    return DocumentMetadata(**doc)

@router.post("/documents/ingest")
async def ingest_document(
    file: UploadFile = File(...),
    doc_id: str = Form(...),
    title: str = Form(...),
    organization: str = Form(...),
    document_type: str = Form("guideline"),
    disease_category: str = Form("General"),
    publication_date: str = Form(""),
    source_url: str = Form(...)
):
    """Admin endpoint to upload and ingest an authorized PDF document."""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported for ingestion.")

    save_dir = "data/raw"
    os.makedirs(save_dir, exist_ok=True)
    file_path = os.path.join(save_dir, f"{doc_id}_{file.filename}")

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        pages = ingestion_manager.extract_pdf_pages(file_path)
        if not pages:
            raise HTTPException(status_code=422, detail="Failed to extract readable text from PDF.")

        chunks_count = ingestion_manager.ingest_document_data(
            doc_id=doc_id,
            title=title,
            organization=organization,
            doc_type=document_type,
            category=disease_category,
            pub_date=publication_date,
            url=source_url,
            pages=pages,
            file_path=file_path
        )

        return {
            "status": "success",
            "message": f"Successfully ingested {chunks_count} chunks from '{title}'.",
            "document_id": doc_id,
            "chunks_count": chunks_count
        }
    except Exception as e:
        logger.error(f"Error ingesting document {doc_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

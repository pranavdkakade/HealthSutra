from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.config import settings
from app.database.session import get_db, engine
from app.services.retrieval import VectorStoreService
from app.services.ingestion import IngestionManager
from app.schemas.api_schemas import SystemHealthResponse

router = APIRouter()

@router.get("/health", response_model=SystemHealthResponse)
def get_system_health(db: Session = Depends(get_db)):
    vector_store = VectorStoreService.get_instance()
    ingestion = IngestionManager()

    db_ok = False
    try:
        with engine.connect() as conn:
            db_ok = True
    except Exception:
        db_ok = False

    return SystemHealthResponse(
        status="healthy",
        app_name=settings.APP_NAME,
        version="1.0.0",
        faiss_index_loaded=vector_store.index is not None,
        total_chunks_indexed=vector_store.index.ntotal if vector_store.index else 0,
        total_documents_registered=len(ingestion.registry),
        database_connected=db_ok,
        embedding_model_loaded=vector_store.embedding_service._model is not None
    )

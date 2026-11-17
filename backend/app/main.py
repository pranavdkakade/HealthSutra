import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database.session import init_db
from app.services.ingestion import IngestionManager
from app.api.chat import router as chat_router
from app.api.documents import router as documents_router
from app.api.feedback import router as feedback_router
from app.api.health import router as health_router
from app.api.evaluation import router as evaluation_router
from app.api.admin import router as admin_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("healthsutra.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup sequence
    logger.info(f"Starting {settings.APP_NAME} in {settings.APP_ENV} mode...")
    
    # 1. Initialize DB tables
    init_db()

    # 2. Seed initial WHO & MoHFW knowledge base into FAISS
    ingestion = IngestionManager()
    seeded = ingestion.seed_initial_knowledge()
    logger.info(f"Verified knowledge base ready with {len(ingestion.registry)} documents.")

    yield
    # Shutdown sequence
    logger.info(f"Shutting down {settings.APP_NAME}...")

app = FastAPI(
    title=settings.APP_NAME,
    description="SIH25049 - Public Health Awareness Chatbot with Document-Grounded RAG and Verifiable Citations",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(health_router, prefix="/api/v1", tags=["Health & Status"])
app.include_router(chat_router, prefix="/api/v1", tags=["Chat & Grounded Query"])
app.include_router(documents_router, prefix="/api/v1", tags=["Documents & Knowledge"])
app.include_router(feedback_router, prefix="/api/v1", tags=["Citizen Feedback"])
app.include_router(evaluation_router, prefix="/api/v1", tags=["Evaluation"])
app.include_router(admin_router, prefix="/api/v1", tags=["Admin Analytics"])

@app.get("/")
def root():
    return {
        "project": settings.APP_NAME,
        "theme": "SIH25049 Public Health Awareness Chatbot",
        "status": "online",
        "docs_url": "/docs",
        "api_v1": "/api/v1"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)

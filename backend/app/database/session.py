import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

logger = logging.getLogger("healthsutra.database")

Base = declarative_base()

def get_engine():
    db_url = settings.DATABASE_URL
    try:
        if db_url.startswith("postgresql"):
            logger.info(f"Connecting to PostgreSQL: {db_url.split('@')[-1] if '@' in db_url else 'configured'}")
            engine = create_engine(db_url, pool_pre_ping=True)
            # Test connection
            with engine.connect() as conn:
                pass
            return engine
    except Exception as e:
        logger.warning(f"PostgreSQL connection failed ({e}). Falling back to SQLite.")
    
    # Fallback to SQLite
    os.makedirs("data", exist_ok=True)
    sqlite_url = "sqlite:///./data/healthsutra.db"
    logger.info(f"Using SQLite database engine at {sqlite_url}")
    return create_engine(
        sqlite_url,
        connect_args={"check_same_thread": False}
    )

engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    from app.models.database_models import DocumentModel, DocumentChunkModel, QueryLogModel, CitationModel, FeedbackModel, EvaluationRunModel
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized successfully.")

import datetime
import uuid
from sqlalchemy import Column, String, Integer, Float, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database.session import Base


def utc_now():
    return datetime.datetime.now(datetime.UTC)

class DocumentModel(Base):
    __tablename__ = "documents"

    id = Column(String(64), primary_key=True)
    title = Column(String(255), nullable=False)
    organization = Column(String(64), nullable=False) # 'WHO', 'MoHFW', 'ICMR', 'NHM'
    document_type = Column(String(64), nullable=False) # 'fact_sheet', 'guideline', 'advisory'
    disease_category = Column(String(128), default="General")
    publication_date = Column(String(32), default="")
    source_url = Column(Text, nullable=False)
    file_path = Column(Text, default="")
    verified = Column(Boolean, default=True)
    language = Column(String(10), default="en")
    created_at = Column(DateTime, default=utc_now)

    chunks = relationship("DocumentChunkModel", back_populates="document", cascade="all, delete-orphan")


class DocumentChunkModel(Base):
    __tablename__ = "document_chunks"

    id = Column(String(128), primary_key=True)
    document_id = Column(String(64), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    page_number = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    token_count = Column(Integer, default=0)
    content_hash = Column(String(64), default="")
    created_at = Column(DateTime, default=utc_now)

    document = relationship("DocumentModel", back_populates="chunks")


class QueryLogModel(Base):
    __tablename__ = "query_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(64), nullable=True)
    user_question = Column(Text, nullable=False)
    detected_language = Column(String(10), default="en")
    response_status = Column(String(32), nullable=False) # 'answered', 'insufficient_evidence', 'emergency_alert'
    generated_answer = Column(Text, nullable=True)
    top_similarity_score = Column(Float, default=0.0)
    latency_ms = Column(Float, default=0.0)
    safety_flags = Column(Text, default="")
    created_at = Column(DateTime, default=utc_now)

    citations = relationship("CitationModel", back_populates="query_log", cascade="all, delete-orphan")
    feedback = relationship("FeedbackModel", back_populates="query_log", cascade="all, delete-orphan")


class CitationModel(Base):
    __tablename__ = "citations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    query_log_id = Column(String(36), ForeignKey("query_logs.id", ondelete="CASCADE"), nullable=False)
    chunk_id = Column(String(128), ForeignKey("document_chunks.id", ondelete="SET NULL"), nullable=True)
    document_id = Column(String(64), ForeignKey("documents.id", ondelete="SET NULL"), nullable=True)
    page_number = Column(Integer, default=1)
    confidence_score = Column(Float, default=0.0)
    verified_by_backend = Column(Boolean, default=False)

    query_log = relationship("QueryLogModel", back_populates="citations")


class FeedbackModel(Base):
    __tablename__ = "feedback"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    query_log_id = Column(String(36), ForeignKey("query_logs.id", ondelete="CASCADE"), nullable=True)
    user_question = Column(Text, nullable=True)
    generated_answer = Column(Text, nullable=True)
    rating = Column(Integer, nullable=False) # 1 for helpful, -1 for unhelpful
    comment = Column(Text, default="")
    created_at = Column(DateTime, default=utc_now)

    query_log = relationship("QueryLogModel", back_populates="feedback")


class EvaluationRunModel(Base):
    __tablename__ = "evaluation_runs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    benchmark_name = Column(String(128), nullable=False)
    model_used = Column(String(64), nullable=False)
    total_questions = Column(Integer, nullable=False)
    answered_count = Column(Integer, nullable=False)
    refused_count = Column(Integer, nullable=False)
    groundedness_score = Column(Float, nullable=False)
    citation_precision = Column(Float, nullable=False)
    unsupported_claim_rate = Column(Float, nullable=False)
    results_payload = Column(JSON, nullable=True)
    run_at = Column(DateTime, default=utc_now)

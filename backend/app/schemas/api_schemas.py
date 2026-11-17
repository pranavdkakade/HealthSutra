from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class Citation(BaseModel):
    document_id: str
    document_title: str
    organization: str
    page: int
    source_url: str
    confidence_score: Optional[float] = 0.0
    snippet: Optional[str] = ""

class ChatRequest(BaseModel):
    question: str = Field(..., min_length=2, max_length=2000, description="Citizen health question")
    language: Optional[str] = Field("en", description="Preferred response language ('en', 'hi', 'mr')")
    session_id: Optional[str] = Field(None, description="Optional client session identifier")

class ChatResponse(BaseModel):
    status: str = Field(..., description="'answered', 'insufficient_evidence', 'emergency_alert', or 'safety_violation'")
    answer: str
    language: str
    citations: List[Citation] = []
    safety_notice: str
    top_score: float = 0.0
    latency_ms: float = 0.0
    grounded: bool = True

class DocumentMetadata(BaseModel):
    id: str
    title: str
    organization: str
    document_type: str
    disease_category: Optional[str] = "General Health"
    publication_date: Optional[str] = ""
    source_url: str
    file_path: Optional[str] = ""
    verified: bool = True
    language: str = "en"
    chunks_count: Optional[int] = 0

class DocumentListResponse(BaseModel):
    total_documents: int
    documents: List[DocumentMetadata]

class IngestDocumentRequest(BaseModel):
    id: str
    title: str
    organization: str
    document_type: str
    disease_category: Optional[str] = "General"
    publication_date: Optional[str] = ""
    source_url: str
    file_path: Optional[str] = None
    language: Optional[str] = "en"

class FeedbackRequest(BaseModel):
    query_log_id: Optional[str] = None
    question: Optional[str] = None
    answer: Optional[str] = None
    rating: int = Field(..., ge=-1, le=1, description="1 for helpful, -1 for unhelpful")
    comment: Optional[str] = ""

class FeedbackResponse(BaseModel):
    status: str
    message: str

class SystemHealthResponse(BaseModel):
    status: str
    app_name: str
    version: str
    faiss_index_loaded: bool
    total_chunks_indexed: int
    total_documents_registered: int
    database_connected: bool
    embedding_model_loaded: bool

class BenchmarkQuestion(BaseModel):
    id: str
    question: str
    category: str  # 'answerable', 'missing_info', 'out_of_scope', 'emergency'
    language: str = "en"
    expected_status: str  # 'answered', 'insufficient_evidence', 'emergency_alert'

class EvaluationMetric(BaseModel):
    groundedness_score: float
    citation_precision: float
    unsupported_claim_rate: float
    refusal_accuracy: float
    answer_coverage: float

class EvaluationResponse(BaseModel):
    benchmark_name: str
    total_questions: int
    grounded_system: EvaluationMetric
    ungrounded_system: EvaluationMetric
    comparison_summary: Dict[str, Any]

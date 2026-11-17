import time
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.config import settings
from app.database.session import get_db
from app.schemas.api_schemas import ChatRequest, ChatResponse, Citation
from app.services.safety import SafetyGuard
from app.services.retrieval import VectorStoreService
from app.services.grounding import GroundingValidator
from app.services.generation import GenerationService
from app.models.database_models import QueryLogModel, CitationModel

logger = logging.getLogger("healthsutra.api.chat")
router = APIRouter()

vector_store = VectorStoreService.get_instance()
grounding_validator = GroundingValidator()
generation_service = GenerationService()

@router.post("/chat", response_model=ChatResponse)
def handle_chat_query(req: ChatRequest, db: Session = Depends(get_db)):
    start_time = time.time()
    question = req.question.strip()
    
    # 1. Language detection
    detected_lang = req.language or SafetyGuard.detect_language(question)

    # 2. Safety & Emergency Filter
    is_safe, safety_cat, safety_resp = SafetyGuard.check_query_safety(question)
    if not is_safe and safety_resp:
        latency = (time.time() - start_time) * 1000
        # Log to DB
        log_entry = QueryLogModel(
            session_id=req.session_id,
            user_question=question,
            detected_language=detected_lang,
            response_status=safety_resp["status"],
            generated_answer=safety_resp["answer"],
            top_similarity_score=0.0,
            latency_ms=latency,
            safety_flags=safety_cat
        )
        db.add(log_entry)
        db.commit()

        return ChatResponse(
            status=safety_resp["status"],
            answer=safety_resp["answer"],
            language=safety_resp.get("language", detected_lang),
            citations=[],
            safety_notice=safety_resp["safety_notice"],
            top_score=0.0,
            latency_ms=latency,
            grounded=True
        )

    # 3. Prescription warning check
    prescription_requested = SafetyGuard.check_prescription_request(question)

    # 4. Semantic Document Retrieval from FAISS
    retrieved_chunks = vector_store.search(question, top_k=settings.TOP_K_CHUNKS)

    # 5. Evidence Sufficiency & Calibrated Thresholding
    has_evidence, reason, top_score = grounding_validator.evaluate_evidence(question, retrieved_chunks)

    latency = (time.time() - start_time) * 1000

    if not has_evidence:
        # Refusal Response
        if detected_lang == "hi":
            refusal_text = (
                "मुझे इस प्रश्न का विश्वसनीय उत्तर देने के लिए अपने अनुमोदित विश्व स्वास्थ्य संगठन (WHO) "
                "और भारत सरकार के आधिकारिक स्वास्थ्य दस्तावेजों में पर्याप्त सत्यापित जानकारी नहीं मिली।"
            )
            disclaimer = (
                "हेल्थसूत्र केवल सत्यापित आधिकारिक चिकित्सा दस्तावेजों के आधार पर ही उत्तर देता है। "
                "कृपया सही मार्गदर्शन हेतु किसी योग्य चिकित्सक अथवा नजदीकी प्राथमिक स्वास्थ्य केंद्र (PHC) से संपर्क करें।"
            )
        else:
            refusal_text = (
                "I could not find sufficient verified information in my approved WHO and Government of India "
                "health documents to answer this question reliably."
            )
            disclaimer = (
                "HealthSutra strictly adheres to evidence-based health guidance and refuses to speculate without "
                "verified documentation. Please consult a qualified medical professional or visit your nearest primary health center (PHC)."
            )

        log_entry = QueryLogModel(
            session_id=req.session_id,
            user_question=question,
            detected_language=detected_lang,
            response_status="insufficient_evidence",
            generated_answer=refusal_text,
            top_similarity_score=top_score,
            latency_ms=latency,
            safety_flags="below_evidence_threshold"
        )
        db.add(log_entry)
        db.commit()

        return ChatResponse(
            status="insufficient_evidence",
            answer=refusal_text,
            language=detected_lang,
            citations=[],
            safety_notice=disclaimer,
            top_score=top_score,
            latency_ms=latency,
            grounded=True
        )

    # 6. Grounded Answer Generation
    gen_result = generation_service.generate_grounded_answer(
        question=question,
        retrieved_chunks=retrieved_chunks,
        language=detected_lang
    )

    answer_text = gen_result.get("answer", "")
    citations_data = gen_result.get("citations", [])
    safety_notice = gen_result.get("safety_notice", "")

    # Append prescription caution if user asked about medications
    if prescription_requested:
        if detected_lang == "hi":
            answer_text += (
                "\n\n⚠️ चिकित्सीय सूचना: हेल्थसूत्र किसी भी विशिष्ट दवा या खुराक का नुस्खा नहीं देता है। "
                "दवा लेने से पहले हमेशा किसी योग्य डॉक्टर से परामर्श लें।"
            )
        else:
            answer_text += (
                "\n\n⚠️ Medical Caution: HealthSutra does not provide specific drug prescriptions or dosages. "
                "Always consult a registered physician before taking any medication."
            )

    # 7. Persist to Database with Citations
    log_entry = QueryLogModel(
        session_id=req.session_id,
        user_question=question,
        detected_language=detected_lang,
        response_status="answered",
        generated_answer=answer_text,
        top_similarity_score=top_score,
        latency_ms=latency,
        safety_flags="prescription_caution" if prescription_requested else ""
    )
    db.add(log_entry)
    db.flush()

    for c in citations_data:
        cit_model = CitationModel(
            query_log_id=log_entry.id,
            chunk_id=c.get("document_id"),
            document_id=c.get("document_id"),
            page_number=c.get("page", 1),
            confidence_score=c.get("confidence_score", top_score),
            verified_by_backend=True
        )
        db.add(cit_model)

    db.commit()

    citations_list = [
        Citation(
            document_id=c.get("document_id", "DOC"),
            document_title=c.get("document_title", "Document"),
            organization=c.get("organization", "WHO / MoHFW"),
            page=c.get("page", 1),
            source_url=c.get("source_url", ""),
            confidence_score=c.get("confidence_score", top_score),
            snippet=c.get("snippet", "")
        )
        for c in citations_data
    ]

    return ChatResponse(
        status="answered",
        answer=answer_text,
        language=detected_lang,
        citations=citations_list,
        safety_notice=safety_notice,
        top_score=top_score,
        latency_ms=latency,
        grounded=True
    )

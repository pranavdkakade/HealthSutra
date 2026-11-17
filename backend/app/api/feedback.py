import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.api_schemas import FeedbackRequest, FeedbackResponse
from app.models.database_models import FeedbackModel

logger = logging.getLogger("healthsutra.api.feedback")
router = APIRouter()

@router.post("/feedback", response_model=FeedbackResponse)
def submit_feedback(req: FeedbackRequest, db: Session = Depends(get_db)):
    try:
        feedback_entry = FeedbackModel(
            query_log_id=req.query_log_id,
            user_question=req.question,
            generated_answer=req.answer,
            rating=req.rating,
            comment=req.comment or ""
        )
        db.add(feedback_entry)
        db.commit()
        return FeedbackResponse(status="success", message="Thank you for your feedback.")
    except Exception as e:
        logger.error(f"Error recording feedback: {e}")
        raise HTTPException(status_code=500, detail="Failed to save feedback.")

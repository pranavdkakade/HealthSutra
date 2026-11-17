import datetime
import logging
from sqlalchemy import func
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends
from app.database.session import get_db
from app.models.database_models import QueryLogModel, FeedbackModel

logger = logging.getLogger("healthsutra.api.admin")
router = APIRouter()


@router.get("/admin/analytics")
def get_admin_analytics(db: Session = Depends(get_db)):
    total_queries = db.query(func.count(QueryLogModel.id)).scalar() or 0

    answered_count = (
        db.query(func.count(QueryLogModel.id))
        .filter(QueryLogModel.response_status == "answered")
        .scalar()
        or 0
    )
    refused_count = (
        db.query(func.count(QueryLogModel.id))
        .filter(QueryLogModel.response_status == "insufficient_evidence")
        .scalar()
        or 0
    )
    emergency_count = (
        db.query(func.count(QueryLogModel.id))
        .filter(QueryLogModel.response_status == "emergency_alert")
        .scalar()
        or 0
    )
    safety_blocked_count = (
        db.query(func.count(QueryLogModel.id))
        .filter(QueryLogModel.response_status == "safety_violation")
        .scalar()
        or 0
    )

    avg_latency = db.query(func.avg(QueryLogModel.latency_ms)).scalar() or 0.0
    avg_top_score = db.query(func.avg(QueryLogModel.top_similarity_score)).scalar() or 0.0

    helpful_feedback = (
        db.query(func.count(FeedbackModel.id)).filter(FeedbackModel.rating == 1).scalar() or 0
    )
    unhelpful_feedback = (
        db.query(func.count(FeedbackModel.id)).filter(FeedbackModel.rating == -1).scalar() or 0
    )

    total_feedback = helpful_feedback + unhelpful_feedback
    helpful_ratio = (helpful_feedback / total_feedback) if total_feedback else 0.0

    cutoff = datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=7)
    daily_rows = (
        db.query(func.date(QueryLogModel.created_at).label("day"), func.count(QueryLogModel.id).label("count"))
        .filter(QueryLogModel.created_at >= cutoff)
        .group_by(func.date(QueryLogModel.created_at))
        .order_by(func.date(QueryLogModel.created_at))
        .all()
    )

    daily_traffic = [
        {
            "date": str(row.day),
            "count": int(row.count),
        }
        for row in daily_rows
    ]

    return {
        "totals": {
            "queries": int(total_queries),
            "answered": int(answered_count),
            "refused": int(refused_count),
            "emergency_alerts": int(emergency_count),
            "safety_blocked": int(safety_blocked_count),
            "feedback_total": int(total_feedback),
            "feedback_helpful": int(helpful_feedback),
            "feedback_unhelpful": int(unhelpful_feedback),
        },
        "rates": {
            "answer_rate": (answered_count / total_queries) if total_queries else 0.0,
            "refusal_rate": (refused_count / total_queries) if total_queries else 0.0,
            "helpful_feedback_rate": helpful_ratio,
        },
        "performance": {
            "avg_latency_ms": float(avg_latency),
            "avg_top_similarity_score": float(avg_top_score),
        },
        "traffic_last_7_days": daily_traffic,
    }

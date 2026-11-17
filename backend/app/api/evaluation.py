import json
import logging
from pathlib import Path
from fastapi import APIRouter, HTTPException
from app.schemas.api_schemas import EvaluationResponse, EvaluationMetric

logger = logging.getLogger("healthsutra.api.evaluation")
router = APIRouter()


def _evaluation_summary_path() -> Path:
    # backend/app/api/evaluation.py -> project root -> evaluation/evaluation_summary.json
    return Path(__file__).resolve().parents[3] / "evaluation" / "evaluation_summary.json"


@router.get("/evaluation", response_model=EvaluationResponse)
def get_latest_evaluation():
    summary_path = _evaluation_summary_path()
    if not summary_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Evaluation summary not found. Run evaluation/run_benchmark.py first."
        )

    try:
        with summary_path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        grounded_raw = data.get("healthsutra_rag", {})
        ungrounded_raw = data.get("ungrounded_vanilla", {})

        grounded = EvaluationMetric(
            groundedness_score=float(grounded_raw.get("groundedness_score", 0.0)),
            citation_precision=float(grounded_raw.get("citation_precision", 0.0)),
            unsupported_claim_rate=float(grounded_raw.get("unsupported_claim_rate", 0.0)),
            refusal_accuracy=float(grounded_raw.get("refusal_accuracy", 0.0)),
            answer_coverage=float(grounded_raw.get("answer_coverage", 0.0)),
        )

        ungrounded = EvaluationMetric(
            groundedness_score=float(ungrounded_raw.get("groundedness_score", 0.0)),
            citation_precision=float(ungrounded_raw.get("citation_precision", 0.0)),
            unsupported_claim_rate=float(ungrounded_raw.get("unsupported_claim_rate", 0.0)),
            refusal_accuracy=float(ungrounded_raw.get("refusal_accuracy", 0.0)),
            answer_coverage=float(ungrounded_raw.get("answer_coverage", 0.0)),
        )

        return EvaluationResponse(
            benchmark_name=data.get("benchmark_name", "HealthSutra Evaluation"),
            total_questions=int(data.get("total_questions", 0)),
            grounded_system=grounded,
            ungrounded_system=ungrounded,
            comparison_summary={
                "generated_at": data.get("date", ""),
                "grounded_answered": int(grounded_raw.get("total_answered", 0)),
                "grounded_refused": int(grounded_raw.get("total_refused", 0)),
                "ungrounded_answered": int(ungrounded_raw.get("total_answered", 0)),
                "ungrounded_refused": int(ungrounded_raw.get("total_refused", 0)),
            },
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Failed reading evaluation summary: {exc}")
        raise HTTPException(status_code=500, detail="Failed to load evaluation summary.")

from typing import Any, Dict, List

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..core.deps import get_current_user
from ..db.session import get_db
from ..models.case import Case, CasePriority, CaseStatus
from ..models.user import User

router = APIRouter()


@router.get("/dashboard")
def dashboard(
    db: Session = Depends(get_db), _: User = Depends(get_current_user)
) -> Dict[str, Any]:
    def count_where(column: Any, value: str) -> int:
        return db.query(func.count(Case.id)).filter(column == value).scalar() or 0

    crime_distribution: List[Dict[str, Any]] = [
        {"crime_type": crime_type, "count": count}
        for crime_type, count in db.query(Case.crime_type, func.count(Case.id))
        .group_by(Case.crime_type)
        .all()
    ]
    severity_distribution: List[Dict[str, Any]] = [
        {"priority": priority, "count": count}
        for priority, count in db.query(Case.priority, func.count(Case.id))
        .group_by(Case.priority)
        .all()
    ]

    monthly: Dict[str, int] = {}
    for (created_at,) in db.query(Case.created_at).all():
        key = created_at.strftime("%Y-%m")
        monthly[key] = monthly.get(key, 0) + 1

    officer_performance = [
        {"officer": full_name or username, "cases": count}
        for full_name, username, count in db.query(
            User.full_name, User.username, func.count(Case.id)
        )
        .join(Case, Case.officer_id == User.id)
        .group_by(User.id)
        .all()
    ]

    return {
        "total_cases": db.query(func.count(Case.id)).scalar() or 0,
        "open_cases": count_where(Case.status, CaseStatus.OPEN.value),
        "in_progress_cases": count_where(Case.status, CaseStatus.IN_PROGRESS.value),
        "pending_cases": count_where(Case.status, CaseStatus.PENDING.value),
        "closed_cases": count_where(Case.status, CaseStatus.CLOSED.value),
        "high_priority_cases": count_where(Case.priority, CasePriority.HIGH.value),
        "critical_cases": count_where(Case.priority, CasePriority.CRITICAL.value),
        "total_loss_amount": db.query(func.coalesce(func.sum(Case.loss_amount), 0)).scalar() or 0,
        "crime_distribution": crime_distribution,
        "severity_distribution": severity_distribution,
        "monthly_trend": [
            {"month": month, "count": monthly[month]} for month in sorted(monthly)
        ],
        "officer_performance": officer_performance,
    }


@router.get("/recent-activity")
def recent_activity(
    limit: int = 10, db: Session = Depends(get_db), _: User = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    cases = db.query(Case).order_by(Case.updated_at.desc()).limit(limit).all()
    return [
        {
            "case_id": case.id,
            "case_number": case.case_number,
            "title": case.title,
            "status": case.status,
            "priority": case.priority,
            "updated_at": case.updated_at,
        }
        for case in cases
    ]

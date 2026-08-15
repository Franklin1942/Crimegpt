from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from ..core.deps import get_current_user, record_audit, require_roles
from ..db.session import get_db
from ..models.case import Case, CaseStatus
from ..models.notification import Notification
from ..models.user import User, UserRole
from ..schemas.case import CaseCreate, CaseOut, CaseUpdate

router = APIRouter()


def generate_case_number(db: Session) -> str:
    year = datetime.now(timezone.utc).year
    count = db.query(func.count(Case.id)).scalar() or 0
    return f"CG-{year}-{count + 1:05d}"


def get_case_or_404(db: Session, case_id: int) -> Case:
    case = db.get(Case, case_id)
    if case is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    return case


@router.get("", response_model=List[CaseOut])
def list_cases(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
    status_filter: Optional[CaseStatus] = Query(default=None, alias="status"),
    crime_type: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = Query(default=50, le=200),
    offset: int = 0,
) -> List[Case]:
    query = db.query(Case)
    if status_filter:
        query = query.filter(Case.status == status_filter.value)
    if crime_type:
        query = query.filter(Case.crime_type == crime_type)
    if search:
        pattern = f"%{search}%"
        query = query.filter(
            or_(
                Case.title.ilike(pattern),
                Case.description.ilike(pattern),
                Case.case_number.ilike(pattern),
                Case.complainant_name.ilike(pattern),
            )
        )
    return query.order_by(Case.created_at.desc()).offset(offset).limit(limit).all()


@router.post("", response_model=CaseOut, status_code=status.HTTP_201_CREATED)
def create_case(
    payload: CaseCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.OFFICER)),
) -> Case:
    case = Case(
        case_number=generate_case_number(db),
        officer_id=payload.officer_id or current_user.id,
        **payload.model_dump(exclude={"officer_id", "crime_type", "priority"}),
        crime_type=payload.crime_type.value,
        priority=payload.priority.value,
    )
    db.add(case)
    db.commit()
    db.refresh(case)

    db.add(
        Notification(
            user_id=case.officer_id or current_user.id,
            case_id=case.id,
            title=f"New case assigned: {case.case_number}",
            message=case.title,
            severity="info",
        )
    )
    db.commit()
    record_audit(db, current_user, "create_case", "case", case.id, case.case_number, request)
    return case


@router.get("/{case_id}", response_model=CaseOut)
def get_case(
    case_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)
) -> Case:
    return get_case_or_404(db, case_id)


@router.patch("/{case_id}", response_model=CaseOut)
def update_case(
    case_id: int,
    payload: CaseUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.OFFICER)),
) -> Case:
    case = get_case_or_404(db, case_id)
    data = payload.model_dump(exclude_unset=True)
    for field in ("crime_type", "priority", "status"):
        if data.get(field) is not None:
            data[field] = data[field].value
    for field, value in data.items():
        setattr(case, field, value)
    db.commit()
    db.refresh(case)
    record_audit(db, current_user, "update_case", "case", case.id, case.case_number, request)
    return case


@router.delete("/{case_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_case(
    case_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
) -> None:
    case = get_case_or_404(db, case_id)
    case_number = case.case_number
    db.delete(case)
    db.commit()
    record_audit(db, current_user, "delete_case", "case", case_id, case_number, request)

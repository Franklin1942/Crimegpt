from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..core.deps import get_current_user
from ..db.session import get_db
from ..models.case import CrimeType
from ..models.user import User
from ..services import legal_service
from .cases import get_case_or_404

router = APIRouter()


class LegalRequest(BaseModel):
    crime_type: CrimeType = CrimeType.OTHER
    description: str = ""


@router.get("/crime-types", response_model=List[str])
def crime_types(_: User = Depends(get_current_user)) -> List[str]:
    return [crime.value for crime in CrimeType]


@router.post("/recommend")
def recommend(
    payload: LegalRequest, _: User = Depends(get_current_user)
) -> Dict[str, Any]:
    return {
        "crime_type": payload.crime_type.value,
        "sections": legal_service.recommend_sections(payload.crime_type.value, payload.description),
    }


@router.get("/evidence-checklist")
def evidence_checklist(
    crime_type: CrimeType = CrimeType.OTHER,
    case_id: Optional[int] = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> Dict[str, Any]:
    resolved = crime_type.value
    if case_id is not None:
        resolved = get_case_or_404(db, case_id).crime_type
    return {"crime_type": resolved, "items": legal_service.evidence_checklist(resolved)}

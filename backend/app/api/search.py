from typing import Any, Dict

from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..core.deps import get_current_user
from ..db.session import get_db
from ..models.case import Case
from ..models.document import Document
from ..models.user import User

router = APIRouter()


@router.get("")
def global_search(
    q: str = Query(min_length=2),
    limit: int = 20,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> Dict[str, Any]:
    pattern = f"%{q}%"
    cases = (
        db.query(Case)
        .filter(
            or_(
                Case.title.ilike(pattern),
                Case.description.ilike(pattern),
                Case.case_number.ilike(pattern),
                Case.complainant_name.ilike(pattern),
            )
        )
        .limit(limit)
        .all()
    )
    documents = (
        db.query(Document)
        .filter(or_(Document.filename.ilike(pattern), Document.extracted_text.ilike(pattern)))
        .limit(limit)
        .all()
    )
    return {
        "query": q,
        "cases": [
            {
                "id": case.id,
                "case_number": case.case_number,
                "title": case.title,
                "status": case.status,
            }
            for case in cases
        ],
        "documents": [
            {"id": doc.id, "case_id": doc.case_id, "filename": doc.filename} for doc in documents
        ],
    }

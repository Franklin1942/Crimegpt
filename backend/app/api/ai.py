from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from ..core.deps import get_current_user, record_audit
from ..db.session import get_db
from ..models.document import Document, DocumentAnalysis
from ..models.notification import Notification
from ..models.user import User
from ..schemas.document import DocumentAnalysisOut, TextAnalysisRequest
from ..services import ai_service
from .cases import get_case_or_404

router = APIRouter()


@router.post("/analyze-text")
def analyze_text(
    payload: TextAnalysisRequest, _: User = Depends(get_current_user)
) -> Dict[str, Any]:
    return ai_service.analyze_text(payload.text)


@router.post("/documents/{document_id}/analyze", response_model=DocumentAnalysisOut)
def analyze_document(
    document_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DocumentAnalysis:
    document = db.get(Document, document_id)
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    case = get_case_or_404(db, document.case_id)
    result = ai_service.analyze_text(document.extracted_text or case.description)

    analysis = document.analysis or DocumentAnalysis(
        document_id=document.id, case_id=document.case_id
    )
    analysis.crime_type = result["crime_type"]
    analysis.confidence = result["confidence"]
    analysis.summary = result["summary"]
    analysis.entities = result["entities"]
    analysis.timeline = result["timeline"]
    analysis.recommendations = result["recommendations"]
    analysis.legal_sections = result["legal_sections"]
    analysis.engine = result["engine"]
    db.add(analysis)

    if case.crime_type == "other" and result["crime_type"] != "other":
        case.crime_type = result["crime_type"]

    db.add(
        Notification(
            user_id=current_user.id,
            case_id=case.id,
            title=f"AI analysis complete for {case.case_number}",
            message=result["summary"][:255],
            severity="success",
        )
    )
    db.commit()
    db.refresh(analysis)
    record_audit(
        db, current_user, "analyze_document", "document", document.id, result["crime_type"], request
    )
    return analysis


@router.get("/cases/{case_id}/analyses", response_model=List[DocumentAnalysisOut])
def list_case_analyses(
    case_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)
) -> List[DocumentAnalysis]:
    get_case_or_404(db, case_id)
    return (
        db.query(DocumentAnalysis)
        .filter(DocumentAnalysis.case_id == case_id)
        .order_by(DocumentAnalysis.created_at.desc())
        .all()
    )

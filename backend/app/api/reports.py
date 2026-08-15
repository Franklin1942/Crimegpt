from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session

from ..core.deps import get_current_user, record_audit
from ..db.session import get_db
from ..models.document import DocumentAnalysis
from ..models.user import User
from ..services import report_service
from .cases import get_case_or_404

router = APIRouter()


@router.get("/cases/{case_id}/charge-sheet")
def charge_sheet(
    case_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    case = get_case_or_404(db, case_id)
    analyses = [
        {"summary": analysis.summary, "recommendations": analysis.recommendations}
        for analysis in db.query(DocumentAnalysis)
        .filter(DocumentAnalysis.case_id == case_id)
        .order_by(DocumentAnalysis.created_at.desc())
        .all()
    ]
    pdf = report_service.build_charge_sheet(case, analyses)
    record_audit(
        db, current_user, "generate_charge_sheet", "case", case.id, case.case_number, request
    )
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="charge-sheet-{case.case_number}.pdf"'
        },
    )

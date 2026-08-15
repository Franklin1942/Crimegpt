import os
import uuid
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status
from sqlalchemy.orm import Session

from ..core.config import settings
from ..core.deps import get_current_user, record_audit
from ..db.session import get_db
from ..models.document import Document
from ..models.user import User
from ..schemas.document import DocumentOut
from ..services import document_service
from .cases import get_case_or_404

router = APIRouter()


@router.get("/case/{case_id}", response_model=List[DocumentOut])
def list_case_documents(
    case_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)
) -> List[Document]:
    get_case_or_404(db, case_id)
    return (
        db.query(Document)
        .filter(Document.case_id == case_id)
        .order_by(Document.created_at.desc())
        .all()
    )


@router.post("/case/{case_id}", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
async def upload_document(
    case_id: int,
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Document:
    get_case_or_404(db, case_id)
    content = await file.read()
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds the {settings.MAX_UPLOAD_SIZE_MB}MB limit",
        )

    case_dir = os.path.join(settings.UPLOAD_DIR, str(case_id))
    os.makedirs(case_dir, exist_ok=True)
    safe_name = os.path.basename(file.filename or "upload.bin")
    storage_path = os.path.join(case_dir, f"{uuid.uuid4().hex}_{safe_name}")
    with open(storage_path, "wb") as handle:
        handle.write(content)

    document = Document(
        case_id=case_id,
        filename=safe_name,
        content_type=file.content_type or "application/octet-stream",
        size_bytes=len(content),
        storage_path=storage_path,
        extracted_text=document_service.extract_text(safe_name, content, file.content_type),
        uploaded_by=current_user.id,
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    record_audit(
        db, current_user, "upload_document", "document", document.id, safe_name, request
    )
    return document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    document = db.get(Document, document_id)
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    if document.storage_path and os.path.exists(document.storage_path):
        os.remove(document.storage_path)
    db.delete(document)
    db.commit()
    record_audit(db, current_user, "delete_document", "document", document_id, request=request)

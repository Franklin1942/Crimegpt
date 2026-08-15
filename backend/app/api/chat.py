from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..core.deps import get_current_user
from ..db.session import get_db
from ..models.chat import ChatMessage, ChatSession
from ..models.user import User
from ..schemas.chat import ChatRequest, ChatResponse, ChatSessionOut
from ..services import chat_service
from .cases import get_case_or_404

router = APIRouter()

HISTORY_LIMIT = 10


@router.get("/sessions", response_model=List[ChatSessionOut])
def list_sessions(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> List[ChatSession]:
    return (
        db.query(ChatSession)
        .filter(ChatSession.user_id == current_user.id)
        .order_by(ChatSession.created_at.desc())
        .all()
    )


@router.get("/sessions/{session_id}", response_model=ChatSessionOut)
def get_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ChatSession:
    session = db.get(ChatSession, session_id)
    if session is None or session.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return session


@router.post("", response_model=ChatResponse)
def send_message(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ChatResponse:
    if payload.session_id:
        session = db.get(ChatSession, payload.session_id)
        if session is None or session.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    else:
        session = ChatSession(
            user_id=current_user.id,
            case_id=payload.case_id,
            title=payload.message[:60] or "New conversation",
        )
        db.add(session)
        db.commit()
        db.refresh(session)

    case_context = None
    case_id = payload.case_id or session.case_id
    if case_id:
        case = get_case_or_404(db, case_id)
        case_context = {
            "case_number": case.case_number,
            "title": case.title,
            "crime_type": case.crime_type,
            "status": case.status,
            "description": case.description[:2000],
        }

    history = [
        {"role": message.role, "content": message.content}
        for message in session.messages[-HISTORY_LIMIT:]
    ]
    result = chat_service.generate_reply(payload.message, history, case_context)

    db.add(ChatMessage(session_id=session.id, role="user", content=payload.message))
    db.add(ChatMessage(session_id=session.id, role="assistant", content=result["reply"]))
    db.commit()

    return ChatResponse(session_id=session.id, reply=result["reply"], engine=result["engine"])

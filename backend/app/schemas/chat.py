from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class ChatRequest(BaseModel):
    message: str
    case_id: Optional[int] = None
    session_id: Optional[int] = None


class ChatMessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role: str
    content: str
    created_at: datetime


class ChatResponse(BaseModel):
    session_id: int
    reply: str
    engine: str


class ChatSessionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    case_id: Optional[int]
    created_at: datetime
    messages: List[ChatMessageOut] = []

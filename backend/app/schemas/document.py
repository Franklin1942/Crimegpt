from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict


class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    case_id: int
    filename: str
    content_type: str
    size_bytes: int
    created_at: datetime


class DocumentAnalysisOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    document_id: int
    case_id: int
    crime_type: str
    confidence: int
    summary: str
    entities: Dict[str, Any]
    timeline: List[Any]
    recommendations: List[Any]
    legal_sections: List[Any]
    engine: str
    created_at: datetime


class TextAnalysisRequest(BaseModel):
    text: str
    case_id: Optional[int] = None

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from ..models.case import CasePriority, CaseStatus, CrimeType


class CaseBase(BaseModel):
    title: str = Field(min_length=3, max_length=255)
    description: str = ""
    crime_type: CrimeType = CrimeType.OTHER
    priority: CasePriority = CasePriority.MEDIUM
    complainant_name: str = ""
    complainant_contact: str = ""
    location: str = ""
    loss_amount: int = 0


class CaseCreate(CaseBase):
    officer_id: Optional[int] = None


class CaseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    crime_type: Optional[CrimeType] = None
    priority: Optional[CasePriority] = None
    status: Optional[CaseStatus] = None
    complainant_name: Optional[str] = None
    complainant_contact: Optional[str] = None
    location: Optional[str] = None
    loss_amount: Optional[int] = None
    officer_id: Optional[int] = None


class CaseOut(CaseBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    case_number: str
    status: CaseStatus
    officer_id: Optional[int]
    created_at: datetime
    updated_at: datetime

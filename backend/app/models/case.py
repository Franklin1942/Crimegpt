from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db.session import Base


class CaseStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    PENDING = "pending"
    CLOSED = "closed"


class CasePriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CrimeType(str, Enum):
    PHISHING = "phishing"
    UPI_FRAUD = "upi_fraud"
    IDENTITY_THEFT = "identity_theft"
    MALWARE = "malware"
    RANSOMWARE = "ransomware"
    SOCIAL_MEDIA_FRAUD = "social_media_fraud"
    SIM_SWAP = "sim_swap"
    FINANCIAL_FRAUD = "financial_fraud"
    CYBER_STALKING = "cyber_stalking"
    DATA_BREACH = "data_breach"
    OTHER = "other"


class Case(Base):
    __tablename__ = "cases"

    id: Mapped[int] = mapped_column(primary_key=True)
    case_number: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text, default="")
    crime_type: Mapped[str] = mapped_column(String(64), default=CrimeType.OTHER.value)
    status: Mapped[str] = mapped_column(String(32), default=CaseStatus.OPEN.value)
    priority: Mapped[str] = mapped_column(String(32), default=CasePriority.MEDIUM.value)
    complainant_name: Mapped[str] = mapped_column(String(255), default="")
    complainant_contact: Mapped[str] = mapped_column(String(64), default="")
    location: Mapped[str] = mapped_column(String(255), default="")
    loss_amount: Mapped[int] = mapped_column(Integer, default=0)
    officer_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    officer: Mapped[Optional["User"]] = relationship(  # noqa: F821
        back_populates="cases", foreign_keys=[officer_id]
    )
    documents: Mapped[list["Document"]] = relationship(  # noqa: F821
        back_populates="case", cascade="all, delete-orphan"
    )

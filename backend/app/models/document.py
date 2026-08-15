from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db.session import Base


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id", ondelete="CASCADE"), index=True)
    filename: Mapped[str] = mapped_column(String(255))
    content_type: Mapped[str] = mapped_column(String(128), default="application/octet-stream")
    size_bytes: Mapped[int] = mapped_column(Integer, default=0)
    storage_path: Mapped[str] = mapped_column(String(512), default="")
    extracted_text: Mapped[str] = mapped_column(Text, default="")
    uploaded_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    case: Mapped["Case"] = relationship(back_populates="documents")  # noqa: F821
    analysis: Mapped[Optional["DocumentAnalysis"]] = relationship(
        back_populates="document", cascade="all, delete-orphan", uselist=False
    )


class DocumentAnalysis(Base):
    __tablename__ = "document_analyses"

    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"), index=True
    )
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id", ondelete="CASCADE"), index=True)
    crime_type: Mapped[str] = mapped_column(String(64), default="other")
    confidence: Mapped[int] = mapped_column(Integer, default=0)
    summary: Mapped[str] = mapped_column(Text, default="")
    entities: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    timeline: Mapped[list[Any]] = mapped_column(JSON, default=list)
    recommendations: Mapped[list[Any]] = mapped_column(JSON, default=list)
    legal_sections: Mapped[list[Any]] = mapped_column(JSON, default=list)
    engine: Mapped[str] = mapped_column(String(32), default="rule_based")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    document: Mapped["Document"] = relationship(back_populates="analysis")

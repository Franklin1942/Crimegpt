from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db.session import Base


class UserRole(str, Enum):
    ADMIN = "administrator"
    OFFICER = "investigating_officer"
    ANALYST = "cyber_analyst"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(255))
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(32), default=UserRole.OFFICER.value)
    department: Mapped[str] = mapped_column(String(255), default="Cyber Crime Branch")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    cases: Mapped[list["Case"]] = relationship(  # noqa: F821
        back_populates="officer", foreign_keys="Case.officer_id"
    )

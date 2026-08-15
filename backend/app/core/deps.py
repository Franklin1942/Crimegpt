from typing import Callable, Iterable, Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from ..db.session import get_db
from ..models.audit import AuditLog
from ..models.user import User, UserRole
from .config import settings
from .security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_PREFIX}/auth/token")


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if payload is None or not payload.get("sub"):
        raise credentials_error

    user = db.query(User).filter(User.username == payload["sub"]).first()
    if user is None or not user.is_active:
        raise credentials_error
    return user


def require_roles(*roles: UserRole) -> Callable[[User], User]:
    allowed: Iterable[str] = {role.value for role in roles}

    def dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action",
            )
        return current_user

    return dependency


def record_audit(
    db: Session,
    user: Optional[User],
    action: str,
    resource_type: str = "",
    resource_id: str = "",
    details: str = "",
    request: Optional[Request] = None,
) -> None:
    log = AuditLog(
        user_id=user.id if user else None,
        action=action,
        resource_type=resource_type,
        resource_id=str(resource_id),
        details=details,
        ip_address=request.client.host if request and request.client else "",
    )
    db.add(log)
    db.commit()

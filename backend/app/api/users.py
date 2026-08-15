from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from ..core.deps import get_current_user, record_audit, require_roles
from ..core.security import hash_password
from ..db.session import get_db
from ..models.user import User, UserRole
from ..schemas.user import UserCreate, UserOut, UserUpdate

router = APIRouter()


@router.get("", response_model=List[UserOut])
def list_users(
    db: Session = Depends(get_db), _: User = Depends(get_current_user)
) -> List[User]:
    return db.query(User).order_by(User.id).all()


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
) -> User:
    exists = (
        db.query(User)
        .filter((User.username == payload.username) | (User.email == payload.email))
        .first()
    )
    if exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Username or email already registered"
        )
    user = User(
        username=payload.username,
        email=payload.email,
        full_name=payload.full_name,
        role=payload.role.value,
        department=payload.department,
        hashed_password=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    record_audit(db, current_user, "create_user", "user", user.id, request=request)
    return user


@router.patch("/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    payload: UserUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    data = payload.model_dump(exclude_unset=True)
    if "password" in data and data["password"]:
        user.hashed_password = hash_password(data.pop("password"))
    else:
        data.pop("password", None)
    if "role" in data and data["role"] is not None:
        user.role = data.pop("role").value
    for field, value in data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    record_audit(db, current_user, "update_user", "user", user.id, request=request)
    return user

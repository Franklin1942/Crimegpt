from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..core.deps import get_current_user, record_audit
from ..core.security import create_access_token, verify_password
from ..db.session import get_db
from ..models.user import User
from ..schemas.user import Token, UserLogin, UserOut

router = APIRouter()


def _authenticate(db: Session, username: str, password: str) -> User:
    user = db.query(User).filter(User.username == username).first()
    if user is None or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password"
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is deactivated")
    return user


@router.post("/login", response_model=Token)
def login(payload: UserLogin, request: Request, db: Session = Depends(get_db)) -> Token:
    user = _authenticate(db, payload.username, payload.password)
    record_audit(db, user, "login", "user", user.id, request=request)
    return Token(
        access_token=create_access_token(user.username, user.role),
        user=UserOut.model_validate(user),
    )


@router.post("/token", response_model=Token)
def login_form(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
) -> Token:
    """OAuth2 password flow endpoint used by the Swagger UI."""
    user = _authenticate(db, form_data.username, form_data.password)
    return Token(
        access_token=create_access_token(user.username, user.role),
        user=UserOut.model_validate(user),
    )


@router.get("/me", response_model=UserOut)
def read_me(current_user: User = Depends(get_current_user)) -> User:
    return current_user

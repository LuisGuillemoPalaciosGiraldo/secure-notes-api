import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import create_access_token, hash_password, verify_password
from app.database import get_db
from app.models import User
from app.schemas import TokenResponse, UserLogin, UserPublic, UserRegister

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegister, db: Session = Depends(get_db)) -> UserPublic:
    try:
        existing_user = db.query(User).filter(User.email == payload.email).first()
        if existing_user:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered.")

        user = User(email=payload.email, password_hash=hash_password(payload.password))
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Unexpected register error: %s", exc)
        raise HTTPException(status_code=500, detail="Internal server error.") from exc


@router.post("/login", response_model=TokenResponse)
def login(payload: UserLogin, db: Session = Depends(get_db)) -> TokenResponse:
    try:
        user = db.query(User).filter(User.email == payload.email).first()
        if not user or not verify_password(payload.password, user.password_hash):
            logger.warning("Auth failure for email: %s", payload.email)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials.")

        token = create_access_token(str(user.id))
        return TokenResponse(access_token=token)
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Unexpected login error: %s", exc)
        raise HTTPException(status_code=500, detail="Internal server error.") from exc

import logging

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.auth import decode_access_token
from app.database import get_db
from app.models import User

logger = logging.getLogger(__name__)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if not user_id:
            logger.warning("Auth failure: JWT without subject.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials.",
            )
        user = db.query(User).filter(User.id == int(user_id)).first()
        if not user:
            logger.warning("Auth failure: user from JWT not found.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials.",
            )
        return user
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Unexpected auth error: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials.",
        ) from exc

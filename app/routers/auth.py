import secrets
from fastapi import APIRouter, Depends, HTTPException
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status
from app.core.database import get_db
from app.crud.user import get_user_by_name, get_user_by_email
from app.schemas.user import UserCreate, UserResponse
from app.crud import user as user_crud
from app.utils.security import create_access_token, verify_password
from pydantic import BaseModel
from app.core.config import settings
from app.models.token import RefreshToken


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", summary="Register a new user")
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    if get_user_by_name(db, user_in.username):  # ✅ username
        raise HTTPException(status_code=400, detail="Username already taken")
    if get_user_by_email(db, user_in.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    user = user_crud.create_user(db, user_in)
    return {"message": "User registered successfully", "id": user.id}


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = user_crud.get_user_by_name(db, form_data.username)  # ✅ username
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    access_token = create_access_token(
        data={"sub": user.username, "role": user.role},  # ✅ changed to username
        expires_delta=access_token_expires
    )

    refresh_token = secrets.token_urlsafe(64)
    expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    db_refresh = RefreshToken(user_id=user.id, token=refresh_token, expires_at=expires_at)
    db.add(db_refresh)
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


class TokenRefreshRequest(BaseModel):
    refresh_token: str


@router.post("/refresh")
def refresh_access_token(body: TokenRefreshRequest, db: Session = Depends(get_db)):
    db_token = db.query(RefreshToken).filter(RefreshToken.token == body.refresh_token).first()
    if not db_token:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    if db_token.expires_at < datetime.utcnow():
        db.delete(db_token)
        db.commit()
        raise HTTPException(status_code=401, detail="Refresh token expired")

    user = db_token.user
    new_access_token = create_access_token(
        data={"sub": user.username, "role": user.role},  # ✅ username
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {"access_token": new_access_token, "token_type": "bearer"}


@router.post("/logout")
def logout(body: TokenRefreshRequest, db: Session = Depends(get_db)):
    db_token = db.query(RefreshToken).filter(RefreshToken.token == body.refresh_token).first()
    if not db_token:
        raise HTTPException(status_code=404, detail="Token not found")
    db.delete(db_token)
    db.commit()
    return {"message": "Logged out successfully"}
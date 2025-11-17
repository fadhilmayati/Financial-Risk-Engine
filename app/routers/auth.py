"""Authentication routes."""
from __future__ import annotations

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.dependencies import DBSession
from app.config import get_settings
from app.models.user import User
from app.security.auth_handler import create_access_token, hash_password, verify_password, verify_token
from app.security.dependencies import oauth2_scheme

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


@router.post("/register")
def register(email: str, password: str, db: DBSession) -> dict:
    """Register a new user."""

    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")
    user = User(email=email, hashed_password=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"id": user.id, "email": user.email}


@router.post("/login")
def login(db: DBSession, form_data: OAuth2PasswordRequestForm = Depends()) -> dict:
    """Authenticate a user and return access token."""

    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    access_token = create_access_token({"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/refresh")
def refresh_token(token: str = Depends(oauth2_scheme)) -> dict:
    """Refresh a token by issuing a new one with the same subject."""

    payload = verify_token(token)
    subject = payload.get("sub")
    if subject is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    new_token = create_access_token({"sub": subject}, expires_delta=timedelta(minutes=settings.access_token_expire_minutes))
    return {"access_token": new_token, "token_type": "bearer"}

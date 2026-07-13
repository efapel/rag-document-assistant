from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app import schemas
from app import models
from app import database
from app.services import auth as auth_service
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(tags=["auth"])


@router.post("/register", response_model=schemas.UserResponse, status_code=201)
def register(
    user_in: schemas.UserCreate,
    session: Session = Depends(database.get_session),
):
    existing = session.exec(
        select(models.User).where(models.User.email == user_in.email)
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    user = models.User(
        email=user_in.email,
        hashed_password=auth_service.hash_password(user_in.password),
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    return user


@router.post("/login", response_model=schemas.Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(database.get_session),
):
    user = session.exec(
        select(models.User).where(models.User.email == form_data.username)
    ).first()

    if not user or not auth_service.verify_password(
        form_data.password, user.hashed_password
    ):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = auth_service.create_access_token(user_id=user.id)
    return {"access_token": token}
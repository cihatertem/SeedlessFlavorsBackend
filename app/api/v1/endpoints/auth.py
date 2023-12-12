from typing import Annotated

from asyncpg.pgproto.pgproto import timedelta
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from api import exceptions
from api import schemas
from core import auth
from core.config import settings
from db import session, models

FormDataAnnotation = Annotated[OAuth2PasswordRequestForm, Depends()]

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/token", response_model=schemas.AccessToken)
async def login(form_data: FormDataAnnotation, session: session.AsyncSession_):
    user = await auth.authenticate_user(
        session, form_data.username, form_data.password
    )
    if not user:
        raise exceptions.BadLoginRequest()

    access_token_expires = timedelta(days=auth.ACCESS_TOKEN_EXPIRE_DAYS)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post(
    "/signup",
    response_model=schemas.UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def sign_up(session: session.AsyncSession_, user: schemas.UserCreate):
    user_dict = user.model_dump()
    input_pin = user_dict.pop("pin")

    if input_pin != settings.PIN:
        raise exceptions.PinError()

    user_dict["password"] = auth.hash_password(user_dict["password"])
    new_user = models.User(**user_dict)
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    return new_user

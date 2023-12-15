from typing import Annotated

from asyncpg.pgproto.pgproto import timedelta
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from api import crud
from api import schemas
from core import auth
from db import session

FormDataAnnotation = Annotated[OAuth2PasswordRequestForm, Depends()]
UserOperation = Annotated[crud.User, Depends(crud.User)]

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/token", response_model=schemas.AccessToken)
async def login(
        form_data: FormDataAnnotation,
        session: session.AsyncSession_,
):
    user = await auth.authenticate_user(
        session, form_data.username, form_data.password
    )
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
async def sign_up(
        user: schemas.UserCreate,
        operation: UserOperation,
):
    return await operation.create_user(user)

from datetime import datetime
from datetime import timedelta
from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api import exceptions
from api import schemas
from core import config
from db import models
from db import session

SECRET_KEY = config.settings.SECRET_KEY
ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 30
ACCESS_TOKEN_EXPIRE_DAYS = 7

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="v1/auth/token")
TokenAnnotation = Annotated[str, Depends(oauth2_scheme)]

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)


async def get_user_from_db(
    session: AsyncSession,
    username: str,
) -> models.User | None:
    stmt = select(models.User).where(models.User.username == username)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    return user


async def authenticate_user(
    session: AsyncSession,
    username: str,
    password: str,
) -> models.User | bool:
    user = await get_user_from_db(session, username)

    if user is None:
        return False
    if not verify_password(password, user.password):
        return False

    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    session: session.AsyncSession_,
    token: Annotated[str, Depends(oauth2_scheme)],
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")

        if username is None:
            raise exceptions.UnauthorizedRequest()

        token_data = schemas.AccessTokenData(username=username)
    except JWTError:
        raise exceptions.UnauthorizedRequest()

    user = await get_user_from_db(session, username=token_data.username)

    if user is None:
        raise exceptions.UnauthorizedRequest()

    return user


CurrentUserAnnotation = Annotated["USERSCHEMA", Depends(get_current_user)]

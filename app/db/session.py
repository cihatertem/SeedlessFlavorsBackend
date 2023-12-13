# app/db/session.py
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, Depends
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)

from core.config import settings
from db import models

DATABASE_URL = URL.create(
    drivername="postgresql+asyncpg",
    username=settings.POSTGRES_USER,
    password=settings.POSTGRES_PASSWORD,
    host=settings.POSTGRES_HOST,
    port=settings.POSTGRES_PORT,
    database=settings.POSTGRES_DB,
)

engine = create_async_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    # echo=True,
)

async_session = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)


async def get_session():
    session = async_session()
    try:
        yield session
    finally:
        await session.close()


AsyncSession_ = Annotated[AsyncSession, Depends(get_session)]


@asynccontextmanager
async def lifespan(app: FastAPI):
    # TODO after alembic setup this lifespan will be removed!
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
        yield

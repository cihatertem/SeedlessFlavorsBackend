# app/db/session.py
from contextlib import asynccontextmanager
from typing import Annotated

from core.config import settings
from fastapi import FastAPI, Depends
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)

from .models import Base

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
    echo=True,
)

async_session = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)


async def get_session():
    async with async_session() as session:
        yield session


AsyncSession_ = Annotated[AsyncSession, Depends(get_session)]


@asynccontextmanager
async def lifespan(app: FastAPI):
    # TODO after alembic setup this lifespan will be removed!
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        yield

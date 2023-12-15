from datetime import timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from api import crud
from app.main import app
from core import auth
from core.auth import hash_password
from db import models
from db.models import Base
from db.session import engine, async_session


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(scope="class", autouse=True)
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def session():
    new_session = async_session()
    try:
        yield new_session
    finally:
        await new_session.close()


@pytest.fixture(scope="class")
async def class_session():
    new_session = async_session()
    try:
        yield new_session
    finally:
        await new_session.close()


@pytest.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def async_client_authed(access_token_header: dict):
    async with AsyncClient(
            app=app, base_url="http://test", headers=access_token_header
    ) as ac:
        yield ac


@pytest.fixture(scope="class", autouse=True)
async def register_user(class_session: AsyncSession) -> None:
    new_user = models.User(
        first_name="test",
        last_name="user",
        password=hash_password("aBcdef12*G"),
        username="testuser",
        email="test@example.com",
    )

    class_session.add(new_user)
    await class_session.commit()


@pytest.fixture
async def registered_user(session: AsyncSession):
    result = await session.get(models.User, 1)
    result.plain_password = "aBcdef12*G"
    return result


@pytest.fixture
async def access_token_header(async_client: AsyncClient) -> dict:
    response = await async_client.post(
        "/v1/auth/token",
        data={"username": "testuser", "password": "aBcdef12*G"},
    )
    data = response.json()
    return {"Authorization": f"Bearer {data['access_token']}"}


@pytest.fixture
def token_with_nonexistent_user() -> str:
    token = auth.create_access_token({"sub": "invaliduser"})
    return token


@pytest.fixture
def token_with_no_subject() -> str:
    token = auth.create_access_token({"no-sub": "invaliduser"})
    return token


@pytest.fixture
def valid_token(registered_user: models.User) -> str:
    token = auth.create_access_token({"sub": registered_user.username})
    return token


@pytest.fixture
def expired_token(registered_user: models.User) -> str:
    token = auth.create_access_token(
        {"sub": registered_user.username},
        timedelta(minutes=-15),
    )
    return token


@pytest.fixture
async def category(session: AsyncSession):
    return crud.Category(session=session)


@pytest.fixture
async def user(session: AsyncSession):
    return crud.User(session=session)


@app.get("/test_integrity", tags=["tests"])
async def test_integrity():
    raise IntegrityError(statement="testing", params=[], orig=Exception())

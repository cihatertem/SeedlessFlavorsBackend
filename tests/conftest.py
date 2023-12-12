import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from core.auth import hash_password
from db import models
from db.models import Base
from db.session import engine, async_session


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(scope="session", autouse=True)
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="session")
async def session():
    async with async_session() as session:
        yield session


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


@pytest.fixture(scope="session", autouse=True)
async def register_user(session: AsyncSession) -> None:
    stmt = select(models.User).where(models.User.username == "testuser")
    result = await session.execute(stmt)

    new_user = models.User(
        first_name="test",
        last_name="user",
        password=hash_password("aBcdef12*G"),
        username="testuser",
        email="test@example.com",
    )

    session.add(new_user)
    await session.commit()


@pytest.fixture
async def access_token_header(
    async_client: AsyncClient, register_user
) -> dict:
    response = await async_client.post(
        "/v1/auth/token",
        data={"username": "testuser", "password": "aBcdef12*G"},
    )
    data = response.json()
    return {"Authorization": f"Bearer {data['access_token']}"}


@app.get("/test_integrity", tags=["tests"])
async def test_integrity():
    raise IntegrityError(statement="testing", params=[], orig=Exception())

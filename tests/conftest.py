import pytest
from httpx import AsyncClient
from sqlalchemy.exc import IntegrityError

from app.main import app
from db.models import Base
from db.session import engine, async_session


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(scope="session", autouse=True)
async def setup_test_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@pytest.fixture
async def session():
    async with async_session() as session:
        yield session


@pytest.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@app.get("/test_integrity", tags=["tests"])
async def test_integrity():
    raise IntegrityError(statement="testing", params=[], orig=Exception())

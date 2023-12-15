import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from api import exceptions
from core import auth
from db import models


@pytest.mark.anyio
class CoreAuthOperationsTests:
    async def test_get_user_from_db_with_valid_username(
            self,
            session: AsyncSession,
            registered_user: models.User,
    ):
        result = await auth.get_user_from_db(
            session=session,
            username="testuser",
        )

        assert result.username == registered_user.username

    async def test_user_from_db_with_nonexistent_username(
            self,
            session: AsyncSession,
            registered_user: models.User,
    ):
        result = await auth.get_user_from_db(
            session=session,
            username="nonexistentuser",
        )

        assert result is None

    async def test_authenticate_user_with_valid_credentials(
            self,
            session: AsyncSession,
            registered_user: models.User,
    ):
        user = await auth.authenticate_user(
            session=session,
            username=registered_user.username,
            password=registered_user.plain_password,
        )

        del registered_user.plain_password
        assert user == registered_user

    @pytest.mark.parametrize(
        "credentials",
        [
            {"username": "testuser", "password": "asdfgHj12*"},
            {"username": "nonexistent", "password": "asAedf0*11"},
        ],
    )
    async def test_authenticate_user_with_wrong_credentials(
            self, session: AsyncSession, credentials: dict
    ):
        with pytest.raises(exceptions.BadLoginRequest):
            await auth.authenticate_user(
                session=session,
                username=credentials["username"],
                password=credentials["password"],
            )

    async def test_create_access_token(
            self,
            async_client: AsyncClient,
            registered_user: models.User,
    ):
        token = auth.create_access_token({"sub": registered_user.username})

        response = await async_client.post(
            "/v1/categories",
            json={"name": "new category"},
            headers={"Authorization": f"Bearer {token}"},
        )
        data = response.json()

        assert response.status_code == status.HTTP_201_CREATED
        assert data["name"] == "new category"

    async def test_get_current_user_with_valid_token(
            self,
            session: AsyncSession,
            valid_token: str,
            registered_user: models.User,
    ):
        user = await auth.get_current_user(
            session=session,
            token=valid_token,
        )

        del registered_user.plain_password

        assert user == registered_user

    async def test_get_current_user_with_token_has_no_subject(
            self,
            session: AsyncSession,
            token_with_no_subject: str,
    ):
        with pytest.raises(exceptions.UnauthorizedRequest):
            await auth.get_current_user(
                session=session,
                token=token_with_no_subject,
            )

    async def test_get_current_user_with_token_nonexistent_user(
            self,
            session: AsyncSession,
            token_with_nonexistent_user: str,
    ):
        with pytest.raises(exceptions.UnauthorizedRequest):
            await auth.get_current_user(
                session=session,
                token=token_with_nonexistent_user,
            )

    async def test_get_current_user_with_expired_token(
            self,
            session: AsyncSession,
            expired_token: str,
    ):
        with pytest.raises(exceptions.UnauthorizedRequest):
            await auth.get_current_user(
                session=session,
                token=expired_token,
            )

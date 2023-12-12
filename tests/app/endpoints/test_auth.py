import pytest
from fastapi import status
from httpx import AsyncClient

from core import config


@pytest.mark.anyio
class AuthEndpointTests:
    AUTH_URL = "/v1/auth"

    user_data = {
        "username": "testuser2",
        "email": "testuser2@example.com",
        "first_name": "test",
        "last_name": "user2",
        "password": "aBcbde123*",
        "pin": config.settings.PIN,
    }

    async def test_create_a_new_user_successfully(
        self,
        async_client: AsyncClient,
    ):
        response = await async_client.post(
            self.AUTH_URL + "/signup",
            json=self.user_data,
        )
        data = response.json()

        assert response.status_code == status.HTTP_201_CREATED
        assert data["username"] == "testuser2"
        assert data["full_name"] == "test user2"

    async def test_create_new_user_with_wrong_pin(
        self,
        async_client: AsyncClient,
    ):
        new_user = self.user_data.copy()
        new_user.update({"pin": "123adc2154"})

        print(new_user)
        response = await async_client.post(
            self.AUTH_URL + "/signup",
            json=new_user,
        )

        data = response.json()

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert data["detail"]["message"] == "Wrong pin. Contact to admin!"

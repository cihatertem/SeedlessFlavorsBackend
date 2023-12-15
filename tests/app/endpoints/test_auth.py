import pytest
from fastapi import status
from httpx import AsyncClient
from jose import jwt

from core import config
from core.auth import ALGORITHM
from core.config import settings
from db import models

user_data = {
    "username": "testuser2",
    "email": "testuser2@example.com",
    "first_name": "test",
    "last_name": "user2",
    "password": "aBcbde123*",
    "pin": config.settings.PIN,
}


def remove_key_return_dict(data: dict, key: str):
    new_data = data.copy()
    new_data.pop(key)
    return new_data


def change_key_value_return_dict_copy(data: dict, key: str, new_value: str):
    new_data = data.copy()
    new_data[key] = new_value

    return new_data


@pytest.mark.anyio
class AuthSignupEndpointTests:
    SIGNUP_URL = "/v1/auth/signup"

    async def test_create_a_new_user_successfully(
            self,
            async_client: AsyncClient,
    ):
        response = await async_client.post(
            self.SIGNUP_URL,
            json=user_data,
        )
        data = response.json()

        assert response.status_code == status.HTTP_201_CREATED
        assert data["username"] == "testuser2"
        assert data["full_name"] == "test user2"

    async def test_create_new_user_with_wrong_pin(
            self,
            async_client: AsyncClient,
    ):
        new_user = user_data.copy()
        new_user.update({"pin": "123adc2154"})

        print(new_user)
        response = await async_client.post(
            self.SIGNUP_URL,
            json=new_user,
        )

        data = response.json()

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert data["detail"]["message"] == "Wrong pin. Contact to admin!"

    @pytest.mark.parametrize(
        "incomplete_user_data",
        [
            remove_key_return_dict(user_data, "password"),
            remove_key_return_dict(user_data, "username"),
            remove_key_return_dict(user_data, "email"),
            remove_key_return_dict(user_data, "first_name"),
            remove_key_return_dict(user_data, "last_name"),
        ],
    )
    async def test_create_new_user_without_required_field_should_raise_err(
            self,
            incomplete_user_data: dict,
            async_client: AsyncClient,
    ):
        response = await async_client.post(
            self.SIGNUP_URL,
            json=incomplete_user_data,
        )
        data = response.json()

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert data["detail"][0]["type"] == "missing"

    async def test_create_user_successfully_should_not_response_with_password(
            self,
            async_client: AsyncClient,
    ):
        new_user = user_data.copy()
        new_user["email"] = "testuser3@example.com"
        new_user["username"] = "testuser3"

        response = await async_client.post(
            self.SIGNUP_URL,
            json=new_user,
        )

        data = response.json()

        with pytest.raises(KeyError):
            pssw = data["password"]

    async def test_create_user_with_existent_username_should_raise_err(
            self,
            async_client: AsyncClient,
    ):
        new_user = user_data.copy()
        new_user["email"] = "testuser4@example.com"

        response = await async_client.post(
            self.SIGNUP_URL,
            json=new_user,
        )
        data = response.json()

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Oops!" in data["message"]

    async def test_create_user_with_existent_email_should_raise_err(
            self,
            async_client: AsyncClient,
    ):
        new_user = user_data.copy()
        new_user["username"] = "testuser5"

        response = await async_client.post(
            self.SIGNUP_URL,
            json=new_user,
        )
        data = response.json()

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Oops!" in data["message"]

    @pytest.mark.parametrize(
        "test_pattern",
        [
            "aBcbde1232",  # '#?! @$%^&*-'."
            "aBcbdeaaa*",  # at least 1 digit
            "aacbde123*",  # at least 1 upper
            "BAAAAA123*",  # at least 1 lower,
        ],
    )
    async def test_create_user_password_should_match_regex_pattern(
            self,
            async_client: AsyncClient,
            test_pattern: str,
    ):
        new_user = user_data.copy()
        new_user["email"] = "testuser5@example.com"
        new_user["password"] = test_pattern
        new_user["username"] = "testuser5"

        response = await async_client.post(
            self.SIGNUP_URL,
            json=new_user,
        )
        data = response.json()

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert data["detail"][0]["type"] == "value_error"

    async def test_create_user_password_length_shoudl_more_than_10(
            self,
            async_client: AsyncClient,
    ):
        new_user = user_data.copy()
        new_user["email"] = "testuser5@example.com"
        new_user["password"] = "aBcef123*"
        new_user["username"] = "testuser5"

        response = await async_client.post(
            self.SIGNUP_URL,
            json=new_user,
        )
        data = response.json()

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert data["detail"][0]["type"] == "string_too_short"

    @pytest.mark.parametrize(
        "test_user",
        [
            change_key_value_return_dict_copy(user_data, "username", "u"),
            change_key_value_return_dict_copy(user_data, "first_name", "u"),
            change_key_value_return_dict_copy(user_data, "last_name", "u"),
        ],
    )
    async def test_create_user_username_first_name_last_name_length_should_more_than_2(
            self,
            async_client: AsyncClient,
            test_user: dict,
    ):
        response = await async_client.post(
            self.SIGNUP_URL,
            json=test_user,
        )
        data = response.json()

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert data["detail"][0]["type"] == "string_too_short"

    @pytest.mark.parametrize(
        "test_user",
        [
            change_key_value_return_dict_copy(user_data, "username", "a" * 21),
            change_key_value_return_dict_copy(
                user_data, "first_name", "u" * 21
            ),
            change_key_value_return_dict_copy(
                user_data, "last_name", "u" * 21
            ),
        ],
    )
    async def test_create_user_username_first_name_last_name_length_should_more_than_2(
            self,
            async_client: AsyncClient,
            test_user: dict,
    ):
        response = await async_client.post(
            self.SIGNUP_URL,
            json=test_user,
        )
        data = response.json()

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert data["detail"][0]["type"] == "string_too_long"

    @pytest.mark.parametrize(
        "test_user",
        [
            change_key_value_return_dict_copy(
                user_data, "email", "testexample.com"
            ),
            change_key_value_return_dict_copy(
                user_data, "email", "test@example"
            ),
            change_key_value_return_dict_copy(
                user_data, "email", "@example.com"
            ),
        ],
    )
    async def test_create_user_email_should_proper_email_address(
            self, async_client: AsyncClient, test_user: dict
    ):
        response = await async_client.post(
            self.SIGNUP_URL,
            json=test_user,
        )
        data = response.json()

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert data["detail"][0]["type"] == "value_error"


@pytest.mark.anyio
class AuthLoginEndpointTests:
    LOGIN_URL = "/v1/auth/token"

    async def test_login_successfully(
            self,
            async_client: AsyncClient,
            registered_user: models.User,
    ):
        response = await async_client.post(
            self.LOGIN_URL,
            data={
                "username": registered_user.username,
                "password": registered_user.plain_password,
            },
        )
        data = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert data["token_type"] == "bearer"

    async def test_login_with_json_body_should_response_err(
            self,
            async_client: AsyncClient,
            registered_user: models.User,
    ):
        response = await async_client.post(
            self.LOGIN_URL,
            json={
                "username": registered_user.username,
                "password": registered_user.plain_password,
            },
        )
        data = response.json()

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert data["detail"][0]["type"] == "missing"  # username
        assert data["detail"][1]["type"] == "missing"  # password

    async def test_login_with_wrong_password_should_response_err(
            self,
            async_client: AsyncClient,
            registered_user: models.User,
    ):
        response = await async_client.post(
            self.LOGIN_URL,
            data={
                "username": registered_user.username,
                "password": registered_user.plain_password + "s",
            },
        )
        data = response.json()

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert data["detail"]["message"] == "Incorrect username or password"

    async def test_login_with_nonexistent_user_should_err_response(
            self,
            async_client: AsyncClient,
    ):
        response = await async_client.post(
            self.LOGIN_URL,
            data={
                "username": "nouser",
                "password": "aSdfhjmp1*",
            },
        )
        data = response.json()

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert data["detail"]["message"] == "Incorrect username or password"

    async def test_login_with_valid_credentials_response_valid_access_token(
            self,
            async_client: AsyncClient,
            registered_user: models.User,
    ):
        response = await async_client.post(
            self.LOGIN_URL,
            data={
                "username": registered_user.username,
                "password": registered_user.plain_password,
            },
        )

        data = response.json()
        payload = jwt.decode(
            data["access_token"],
            settings.SECRET_KEY,
            ALGORITHM,
        )

        assert payload["sub"] == registered_user.username

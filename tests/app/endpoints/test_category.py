import time

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from db import models

CATEGORIES_URL = "/v1/categories"
category_names = ["breakfast", "launch", "dinner"]
INTEGRITY_ERROR_MESSAGE = {"message": "Oops! IntegrityError error!"}


async def setup_new_categories(session: AsyncSession):
    categories = [models.Category(name=name) for name in category_names]
    for category in categories:
        session.add(category)
        await session.commit()
        time.sleep(0.002)


@pytest.mark.anyio
class CategoryEndpointWithoutAuthControlTests:
    async def test_get_empty_categories(self, async_client: AsyncClient):
        response = await async_client.get(CATEGORIES_URL)

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    async def test_get_category_by_name_with_empty_categories(
        self, async_client: AsyncClient
    ):
        response = await async_client.get(
            CATEGORIES_URL, params={"name": "breakfast"}
        )
        data = response.json()

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in data["detail"]["message"]

    async def test_get_all_categories(
        self, async_client: AsyncClient, session: AsyncSession
    ):
        await setup_new_categories(session)
        response = await async_client.get(CATEGORIES_URL)

        assert response.status_code == status.HTTP_200_OK

        data = response.json()

        assert len(data) == 3
        assert data[0]["name"] == "breakfast"

    @pytest.mark.parametrize("sort_by", ["name", "date"])
    async def test_get_all_categories_sort_by_name_or_date_asc(
        self, async_client: AsyncClient, sort_by: str
    ):
        response = await async_client.get(
            CATEGORIES_URL, params={"sort_by": sort_by}
        )
        data = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert data[0]["name"] == "breakfast"

    @pytest.mark.parametrize("sort_by", ["-name", "-date"])
    async def test_get_all_categories_sort_by_date_desc(
        self, async_client: AsyncClient, sort_by: str
    ):
        response = await async_client.get(
            CATEGORIES_URL, params={"sort_by": sort_by}
        )
        data = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert data[-1]["name"] == "breakfast"

    @pytest.mark.parametrize("category_name", category_names)
    async def test_get_category_by_name(
        self, async_client: AsyncClient, category_name: str
    ):
        response = await async_client.get(
            CATEGORIES_URL, params={"name": category_name}
        )
        data = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert data["name"] == category_name

    async def test_get_category_by_id(self, async_client: AsyncClient):
        response = await async_client.get(CATEGORIES_URL + "/1")

        assert response.status_code == status.HTTP_200_OK

        data = response.json()

        assert data["name"] == "breakfast"

    async def test_get_nonexistent_category_by_id(
        self, async_client: AsyncClient
    ):
        response = await async_client.get(CATEGORIES_URL + "/123")
        data = response.json()

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Item not found" in data["detail"]["message"]

    @pytest.mark.parametrize("category_id", ["a", "breakfast", 12.2, "12.2"])
    async def test_get_category_by_wrong_id_type(
        self, async_client: AsyncClient, category_id
    ):
        response = await async_client.get(CATEGORIES_URL + f"/{category_id}")
        data = response.json()

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert data["detail"][0]["type"] == "int_parsing"

    @pytest.mark.parametrize("category_id", [-1, "0", -1.0, 0])
    async def test_get_category_by_wrong_id_less_than_1(
        self, async_client: AsyncClient, category_id
    ):
        response = await async_client.get(CATEGORIES_URL + f"/{category_id}")
        data = response.json()

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert data["detail"][0]["type"] == "greater_than"

    async def test_create_new_category_should_need_authorization(
        self, async_client: AsyncClient
    ):
        response = await async_client.post(
            CATEGORIES_URL, json={"name": "fish"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_update_a_category_by_id_need_authorization(
        self, async_client: AsyncClient
    ):
        response = await async_client.put(
            CATEGORIES_URL + "/1", json={"name": "break-fast"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_delete_a_category_by_id_need_authorization(
        self, async_client: AsyncClient
    ):
        response = await async_client.delete(CATEGORIES_URL + "/1")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.anyio
class CategoryEndpointWithAuthControlTests:
    @pytest.mark.parametrize(
        "category_name",
        ["fish", "meat", "chicken"],
    )
    async def test_create_a_category_with_access_token_successfully(
        self,
        category_name: str,
        async_client_authed: AsyncClient,
    ):
        content = {"name": category_name}
        response = await async_client_authed.post(
            CATEGORIES_URL,
            json=content,
        )

        data = response.json()

        assert response.status_code == status.HTTP_201_CREATED
        assert category_name == data["name"]

    async def test_create_an_existent_category_should_response_bad_request(
        self,
        async_client_authed: AsyncClient,
    ):
        response = await async_client_authed.post(
            CATEGORIES_URL,
            json={"name": "fish"},
        )
        data = response.json()

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert data == INTEGRITY_ERROR_MESSAGE

    @pytest.mark.parametrize("category_name", ["", "   ", "u"])
    async def test_create_category_name_less_than_2_length_name(
        self,
        async_client_authed: AsyncClient,
        category_name: str,
    ):
        response = await async_client_authed.post(
            CATEGORIES_URL,
            json={"name": category_name},
        )
        data = response.json()

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert data["detail"][0]["ctx"] == {"min_length": 2}

    @pytest.mark.parametrize(
        "category_name", [" Askdle-Bar  ", "Asdwss  ", "  Asccas Asdwss"]
    )
    async def test_create_category_should_stripped_and_lowered(
        self,
        category_name: str,
        async_client_authed: AsyncClient,
        async_client: AsyncClient,
    ):
        response = await async_client_authed.post(
            CATEGORIES_URL, json={"name": category_name}
        )
        category_id = response.json()["category_id"]
        assert response.status_code == status.HTTP_201_CREATED

        response = await async_client.get(CATEGORIES_URL + f"/{category_id}")
        data = response.json()
        assert category_name.strip().lower() == data["name"]

    async def test_create_category_more_than_20_length_name(
        self, async_client_authed: AsyncClient
    ):
        response = await async_client_authed.post(
            CATEGORIES_URL,
            json={"name": "asdfghjklzxcvbnmqwert"},
        )
        data = response.json()

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert data["detail"][0]["ctx"] == {"max_length": 20}

    async def test_update_category_successfully(
        self,
        async_client_authed: AsyncClient,
        async_client: AsyncClient,
    ):
        changed_category = "changed"
        response = await async_client_authed.put(
            CATEGORIES_URL + "/1",
            json={"name": changed_category},
        )
        data = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert data == {"message": "Category updated!"}

        response = await async_client.get(CATEGORIES_URL + "/1")
        data = response.json()

        assert data["name"] == changed_category

    async def test_update_category_existent_category_name(
        self, async_client_authed: AsyncClient
    ):
        response = await async_client_authed.put(
            CATEGORIES_URL + "/2",
            json={"name": "changed"},
        )

        data = response.json()

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert data == INTEGRITY_ERROR_MESSAGE

    @pytest.mark.parametrize("category_name", ["", "   ", "u"])
    async def test_update_category_less_than_2_length_name(
        self,
        async_client_authed: AsyncClient,
        async_client: AsyncClient,
        category_name: str,
    ):
        response = await async_client_authed.put(
            CATEGORIES_URL + "/1",
            json={"name": category_name},
        )

        data = response.json()

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert data["detail"][0]["ctx"] == {"min_length": 2}

        response = await async_client.get(CATEGORIES_URL + "/1")
        data = response.json()

        assert data["name"] == "changed"

    async def test_update_category_more_than_20_length_name(
        self,
        async_client_authed: AsyncClient,
        async_client: AsyncClient,
    ):
        response = await async_client_authed.put(
            CATEGORIES_URL + "/1", json={"name": "asdfghjkl zxcbnmasdfg"}
        )

        data = response.json()
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert data["detail"][0]["ctx"] == {"max_length": 20}

        response = await async_client.get(CATEGORIES_URL + "/1")
        data = response.json()
        assert data["name"] == "changed"

    async def test_update_category_nonexistent_id(
        self, async_client_authed: AsyncClient
    ):
        response = await async_client_authed.put(
            CATEGORIES_URL + "/1231234214243", json={"name": "no where"}
        )
        data = response.json()

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in data["detail"]["message"]
        assert "1231234214243" in data["detail"]["message"]

    @pytest.mark.parametrize(
        "category_name", [" Askde-Bar  ", "Asdss  ", "  Asccas Asds"]
    )
    async def test_update_category_should_stripped_and_lowered(
        self,
        category_name: str,
        async_client_authed: AsyncClient,
        async_client: AsyncClient,
    ):
        response = await async_client_authed.put(
            CATEGORIES_URL + "/1",
            json={"name": category_name},
        )
        data = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert data["message"] == "Category updated!"

        response = await async_client.get(CATEGORIES_URL + "/1")
        data = response.json()

        assert data["name"] == category_name.strip().lower()

    async def test_delete_category_by_id_successfully(
        self,
        async_client_authed: AsyncClient,
    ):
        response = await async_client_authed.delete(CATEGORIES_URL + "/1")

        assert response.status_code == status.HTTP_204_NO_CONTENT

    async def test_delete_category_by_nonexistent_id(
        self,
        async_client_authed: AsyncClient,
    ):
        response = await async_client_authed.delete(CATEGORIES_URL + "/1")
        data = response.json()

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert data["detail"]["message"] == f"Item not found by id '1'."

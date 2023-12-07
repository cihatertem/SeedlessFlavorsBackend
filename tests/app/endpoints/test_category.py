import time

import pytest
from fastapi import status
from httpx import AsyncClient

from db import models
from db.session import AsyncSession_

category_names = ["breakfast", "launch", "dinner"]


async def setup_new_categories(session: AsyncSession_):
    categories = [models.Category(name=name) for name in category_names]
    for category in categories:
        session.add(category)
        await session.commit()
        time.sleep(0.002)


@pytest.mark.anyio
class CategoryEndpointWithoutAuthControlTests:
    CATEGORIES_URL = "/api_v1/categories"

    async def test_get_empty_categories(self, async_client: AsyncClient):
        response = await async_client.get(self.CATEGORIES_URL)

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    async def test_get_category_by_name_with_empty_categories(
            self, async_client: AsyncClient
    ):
        response = await async_client.get(
            self.CATEGORIES_URL, params={"name": "breakfast"}
        )
        data = response.json()

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in data["detail"]["message"]

    async def test_get_all_categories(
            self, async_client: AsyncClient, session: AsyncSession_
    ):
        await setup_new_categories(session=session)
        response = await async_client.get(self.CATEGORIES_URL)

        assert response.status_code == status.HTTP_200_OK

        data = response.json()

        assert len(data) == 3
        assert data[0]["name"] == "breakfast"

    @pytest.mark.parametrize("sort_by", ["name", "date"])
    async def test_get_all_categories_sort_by_name_or_date_asc(
            self, async_client: AsyncClient, sort_by: str
    ):
        response = await async_client.get(
            self.CATEGORIES_URL, params={"sort_by": sort_by}
        )
        data = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert data[0]["name"] == "breakfast"

    @pytest.mark.parametrize("sort_by", ["-name", "-date"])
    async def test_get_all_categories_sort_by_date_desc(
            self, async_client: AsyncClient, sort_by: str
    ):
        response = await async_client.get(
            self.CATEGORIES_URL, params={"sort_by": sort_by}
        )
        data = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert data[-1]["name"] == "breakfast"

    @pytest.mark.parametrize("category_name", category_names)
    async def test_get_category_by_name(
            self, async_client: AsyncClient, category_name: str
    ):
        response = await async_client.get(
            self.CATEGORIES_URL, params={"name": category_name}
        )
        data = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert data["name"] == category_name

    async def test_get_category_by_id(self, async_client: AsyncClient):
        response = await async_client.get(self.CATEGORIES_URL + "/1")

        assert response.status_code == status.HTTP_200_OK

        data = response.json()

        assert data["name"] == "breakfast"

    async def test_get_non_exists_category_by_id(
            self, async_client: AsyncClient
    ):
        response = await async_client.get(self.CATEGORIES_URL + "/123")
        data = response.json()

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Item not found" in data["detail"]["message"]

    @pytest.mark.parametrize("category_id", ["a", "breakfast", 12.2, "12.2"])
    async def test_get_category_by_wrong_id_type(
            self, async_client: AsyncClient, category_id
    ):
        response = await async_client.get(
            self.CATEGORIES_URL + f"/{category_id}"
        )
        data = response.json()

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert data["detail"][0]["type"] == "int_parsing"

    @pytest.mark.parametrize("category_id", [-1, "0", -1.0, 0])
    async def test_get_category_by_wrong_id_less_than_1(
            self, async_client: AsyncClient, category_id
    ):
        response = await async_client.get(
            self.CATEGORIES_URL + f"/{category_id}"
        )
        data = response.json()

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert data["detail"][0]["type"] == "greater_than"

    @pytest.mark.xfail
    async def test_create_new_category_should_need_authorization(
            self, async_client: AsyncClient
    ):
        response = await async_client.post(
            self.CATEGORIES_URL, data={"name": "fish"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.xfail
    async def test_update_a_category_by_id_need_autjorization(
            self, async_client: AsyncClient
    ):
        response = await async_client.put(
            self.CATEGORIES_URL + "/1", data={"name": "break-fast"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.xfail
    async def test_delete_a_category_by_id_need_authorization(
            self, async_client: AsyncClient
    ):
        response = await async_client.delete(self.CATEGORIES_URL + "/1")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

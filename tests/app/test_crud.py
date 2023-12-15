import time

import pytest
from sqlalchemy.exc import IntegrityError

from api import exceptions, schemas
from api.crud import Category, User
from api.schemas import CategoryCreate
from core.config import settings


@pytest.mark.anyio
class CategoryCRUDOperationsTests:
    async def test_get_empyt_category_list(self, category: Category):
        result = await category.get_all()

        assert result == []

    @pytest.mark.parametrize(
        "category_name",
        [
            "breakfast",
            "launch",
            "dinner",
        ],
    )
    async def test_create_a_valid_category(
            self,
            category: Category,
            category_name: str,
    ):
        category_scheme = CategoryCreate(name=category_name)
        result = await category.create(category=category_scheme)
        time.sleep(0.002)

        assert result.name == category_scheme.name

    async def test_get_categories_sorted_by_name_asc(self, category: Category):
        result = await category.get_all(sort_by="name")

        assert result[-1].name == "launch"

    async def test_get_categories_sorted_by_name_dsc(
            self,
            category: Category,
    ):
        result = await category.get_all(sort_by="-name")

        assert result[0].name == "launch"

    async def test_get_category_by_id(
            self,
            category: Category,
    ):
        result = await category.get_category_by_id(category_id=1)

        assert result.name == "breakfast"

    async def test_get_category_by_nonexistent_id_should_raise_err(
            self,
            category: Category,
    ):
        with pytest.raises(exceptions.ItemNotFound):
            await category.get_category_by_id(category_id=123)

    async def test_get_category_by_name(
            self,
            category: Category,
    ):
        result = await category.get_category_by_name("breakfast")

        assert result.name == "breakfast"

    async def test_get_category_by_nonexistent_name_should_raise_err(
            self,
            category: Category,
    ):
        with pytest.raises(exceptions.ItemNotFound):
            await category.get_category_by_name("nonexistent")

    async def test_create_category_with_existent_name_should_raise_err(
            self,
            category: Category,
    ):
        with pytest.raises(IntegrityError):
            category_scheme = CategoryCreate(name="breakfast")
            await category.create(category_scheme)

    async def test_update_category_by_id(self, category: Category):
        result = await category.update(category_id=1, name="changed")

        assert result == {"message": "Category updated!"}

    #
    async def test_update_category_by_nonexistent_id_should_raise_err(
            self,
            category: Category,
    ):
        with pytest.raises(exceptions.ItemNotFound):
            await category.update(category_id=123, name="nonexistent")

    async def test_update_category_by_existent_name_should_raise_err(
            self,
            category: Category,
    ):
        with pytest.raises(IntegrityError):
            await category.update(category_id=1, name="dinner")

    async def test_delete_category_by_id(
            self,
            category: Category,
    ):
        result = await category.get_category_by_id(1)

        assert result.name == "changed"

        await category.delete(1)

        with pytest.raises(exceptions.ItemNotFound):
            await category.get_category_by_id(1)

    async def test_delete_category_by_nonexistent_id_should_raise_err(
            self,
            category: Category,
    ):
        with pytest.raises(exceptions.ItemNotFound):
            await category.delete(123123)


@pytest.mark.anyio
class UserCRUDOperationsTests:
    async def test_create_user(self, user: User):
        user_body = schemas.UserCreate(
            username="testuser1",
            email="test12@example.com",
            first_name="test12",
            last_name="user",
            password="aBcdef123*",
            pin=settings.PIN,
        )
        new_user = await user.create_user(user_body)

        assert (
                new_user.full_name
                == user_body.first_name + " " + user_body.last_name
        )

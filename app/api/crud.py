# app/api/crud.py

from sqlalchemy import select, delete, desc, update
from sqlalchemy.ext.asyncio import AsyncSession

from db import models
from db.session import AsyncSession_
from . import schemas, exceptions


def sort_category_by_name_or_date(sort_by, stmt):
    if sort_by.endswith("name"):
        if sort_by.startswith("-"):
            stmt = stmt.order_by(desc(models.Category.name))
        else:
            stmt = stmt.order_by(models.Category.name)
    elif sort_by.endswith("date"):
        if sort_by.startswith("-"):
            stmt = stmt.order_by(desc(models.Category.created_at))
        else:
            stmt = stmt.order_by(models.Category.created_at)

    return stmt


class Category:
    def __init__(self, session: AsyncSession_):
        self.session: AsyncSession = session

    async def get_all(self, sort_by: str = None):
        stmt = select(models.Category)

        if sort_by:
            stmt = sort_category_by_name_or_date(sort_by=sort_by, stmt=stmt)

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_category_by_id(self, category_id: int):
        stmt = select(models.Category).where(
            models.Category.category_id == category_id
        )
        result = await self.session.execute(stmt)
        row = result.scalar()

        if row is None:
            raise exceptions.ItemNotFound(
                detail={"message": f"Item not found by id '{category_id}'."}
            )

        return row

    async def get_category_by_name(self, category_name: str):
        stmt = select(models.Category).where(
            models.Category.name == category_name.lower().strip()
        )
        result = await self.session.execute(stmt)
        row = result.scalar()

        if row is None:
            raise exceptions.ItemNotFound(
                detail={
                    "message": f"Item not found by name '{category_name}'."
                }
            )

        return row

    async def create(self, category: schemas.CategoryCreate):
        new_category = models.Category(name=category.name)
        self.session.add(new_category)
        await self.session.commit()
        await self.session.refresh(new_category)
        return new_category

    async def put(self, category_id: int, name: str):
        stmt = (
            update(models.Category)
            .where(models.Category.category_id == category_id)
            .values(name=name)
        )

        await self.session.execute(stmt)
        await self.session.commit()

    async def delete(self, category_id: int):
        stmt = delete(models.Category).where(
            models.Category.category_id == category_id
        )
        result = await self.session.execute(stmt)

        if result.rowcount == 0:
            raise exceptions.ItemNotFound(
                detail={"message": f"Item not found by id '{category_id}'."},
            )

        await self.session.commit()

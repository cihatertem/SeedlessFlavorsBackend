# app/api/crud.py

from sqlalchemy import select, delete, desc, update
from sqlalchemy.ext.asyncio import AsyncSession

from db import models
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
    @staticmethod
    async def get_all(session: AsyncSession, sort_by: str = None):
        stmt = select(models.Category)

        if sort_by:
            stmt = sort_category_by_name_or_date(sort_by=sort_by, stmt=stmt)

        result = await session.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def get_category_by_id(session: AsyncSession, category_id: int):
        stmt = select(models.Category).where(
            models.Category.category_id == category_id
        )
        result = await session.execute(stmt)
        row = result.scalar()

        if row is None:
            raise exceptions.ItemNotFound(
                detail={"message": f"Item not found by id '{category_id}'."}
            )

        return row

    @staticmethod
    async def get_category_by_name(session: AsyncSession, category_name: str):
        stmt = select(models.Category).where(
            models.Category.name == category_name.lower().strip()
        )
        result = await session.execute(stmt)
        row = result.scalar()

        if row is None:
            raise exceptions.ItemNotFound(
                detail={
                    "message": f"Item not found by name '{category_name}'."
                }
            )

        return row

    @staticmethod
    async def create(session: AsyncSession, category: schemas.CategoryCreate):
        new_category = models.Category(name=category.name)
        session.add(new_category)
        await session.commit()
        await session.refresh(new_category)
        return new_category

    @staticmethod
    async def put(session: AsyncSession, category_id: int, name: str):
        stmt = (
            update(models.Category)
            .where(models.Category.category_id == category_id)
            .values(name=name)
        )

        await session.execute(stmt)
        await session.commit()

    @staticmethod
    async def delete(session: AsyncSession, category_id: int):
        stmt = delete(models.Category).where(
            models.Category.category_id == category_id
        )
        result = await session.execute(stmt)

        if result.rowcount == 0:
            raise exceptions.ItemNotFound(
                detail={"message": f"Item not found by id '{category_id}'."},
            )

        await session.commit()

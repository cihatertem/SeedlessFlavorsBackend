from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Body, Query, status
from fastapi.responses import JSONResponse

from api import schemas, crud
from db.session import AsyncSession_

router = APIRouter(prefix="/categories", tags=["categories"])

category_name_reg = r"^[a-z]*$"
CategoryId = Annotated[int, Path(gt=0)]
CategoryBody = Annotated[schemas.CategoryCreate, Body()]
CategoryNameQuery = Annotated[
    str | None, Query(min_length=2, max_length=20, regex=category_name_reg)
]
CategorySortQuery = Annotated[
    str | None, Query(min_length=3, max_length=10, regex=r"^[+-][a-z]*$")
]


@router.get(
    "",
    response_model=list[schemas.Category] | schemas.Category,
)
async def get_all_categories_or_by_name(
        session: AsyncSession_,
        name: CategoryNameQuery = None,
        sort_by: CategorySortQuery = None,
):
    if name is not None:
        return await crud.Category.get_category_by_name(
            session=session, category_name=name
        )

    return await crud.Category.get_all(session=session, sort_by=sort_by)


@router.get(
    "/{category_id}",
    response_model=schemas.Category,
    status_code=status.HTTP_200_OK,
)
async def get_category_by_id(session: AsyncSession_, category_id: CategoryId):
    return await crud.Category.get_category_by_id(
        session=session, category_id=category_id
    )


@router.post(
    "",
    response_model=schemas.Category,
    status_code=status.HTTP_201_CREATED,
)
async def create_category(category: CategoryBody, session: AsyncSession_):
    return await crud.Category.create(session=session, category=category)


@router.put("/{category_id}", status_code=status.HTTP_202_ACCEPTED)
async def delete_catagory(
        session: AsyncSession_, category_id: CategoryId, category: CategoryBody
):
    await crud.Category.put(
        session=session, category_id=category_id, name=category.name
    )

    return JSONResponse({"message": "Category updated!"})


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_category(category_id: CategoryId, session: AsyncSession_):
    await crud.Category.delete(session=session, category_id=category_id)
    return JSONResponse({"message": f"Category with {category_id} deleted!"})

from typing import Annotated

from fastapi import APIRouter, Body, Query, status, Depends, Path

from api import schemas
from api.crud import Category
from core import auth

router = APIRouter(prefix="/categories", tags=["categories"])

#############
# ANNOTATED #
#############

CategoryOperations = Annotated[Category, Depends(Category)]
CategoryId = Annotated[int, Path(gt=0)]
CategoryBody = Annotated[schemas.CategoryCreate, Body()]
CategoryNameQuery = Annotated[
    str | None,
    Query(min_length=2, max_length=20),
]
CategorySortQuery = Annotated[
    str | None,
    Query(
        min_length=3,
        max_length=10,
        pattern=r"^[-]*[a-z]*$",
        description="use 'name' or 'date' for ascending order and add start "
        "'-' for descending order. ",
        examples=[
            {"?sort_by": "name"},
            {"?sort_by": "-name"},
            {"?sort_by": "date"},
            {"?sort_by": "-date"},
        ],
    ),
]


#############
# ENDPOINTS #
#############


@router.get(
    "",
    response_model=list[schemas.Category] | schemas.Category,
)
async def get_all_categories_or_by_name(
    operation: CategoryOperations,
    name: CategoryNameQuery = None,
    sort_by: CategorySortQuery = None,
):
    if name is not None:
        return await operation.get_category_by_name(category_name=name)

    return await operation.get_all(sort_by=sort_by)


@router.get(
    "/{category_id}",
    response_model=schemas.Category,
    status_code=status.HTTP_200_OK,
)
async def get_category_by_id(
    operation: CategoryOperations, category_id: CategoryId
):
    return await operation.get_category_by_id(category_id=category_id)


@router.post(
    "",
    response_model=schemas.Category,
    status_code=status.HTTP_201_CREATED,
)
async def create_category(
    operation: CategoryOperations,
    category: CategoryBody,
    # token: auth.TokenAnnotation,
    current_user: auth.CurrentUserAnnotation,
):
    return await operation.create(category=category)


@router.put("/{category_id}", status_code=status.HTTP_200_OK)
async def update_category(
    operation: CategoryOperations,
    category_id: CategoryId,
    category: CategoryBody,
    current_user: auth.CurrentUserAnnotation,
):
    return await operation.update(category_id=category_id, name=category.name)


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_category(
    operation: CategoryOperations,
    category_id: CategoryId,
    current_user: auth.CurrentUserAnnotation,
):
    await operation.delete(category_id=category_id)

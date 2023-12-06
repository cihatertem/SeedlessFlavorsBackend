# app/api/schemas.py
import datetime
from typing import Annotated

from pydantic import BaseModel, StringConstraints

CategoryName = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        to_lower=True,
        pattern=r"^[a-zA-Z][a-zA-Z -]*[a-zA-Z]$",
        min_length=2,
        max_length=20,
    ),
]


class CategoryBase(BaseModel):
    name: CategoryName


class CategoryCreate(CategoryBase):
    pass


class Category(CategoryBase):
    category_id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime

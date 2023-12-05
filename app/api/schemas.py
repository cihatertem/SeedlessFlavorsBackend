# app/api/schemas.py
import datetime

from pydantic import BaseModel, constr


class CategoryBase(BaseModel):
    name: constr(
        strip_whitespace=True, to_lower=True, min_length=2, max_length=20
    )


class CategoryCreate(CategoryBase):
    pass


class Category(CategoryBase):
    category_id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime

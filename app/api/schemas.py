# app/api/schemas.py
import datetime
from typing import Annotated

from pydantic import (
    BaseModel,
    StringConstraints,
    EmailStr,
    Field,
    field_validator,
)

CategoryNameAnnotation = Annotated[
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
    name: CategoryNameAnnotation


class CategoryCreate(CategoryBase):
    pass


class Category(CategoryBase):
    category_id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime


class AccessToken(BaseModel):
    access_token: str
    token_type: str


class AccessTokenData(BaseModel):
    username: str | None = None


class UserBase(BaseModel):
    username: str = Field(min_length=2, max_length=20)
    email: EmailStr
    first_name: str = Field(min_length=2, max_length=20)
    last_name: str = Field(min_length=2, max_length=20)


class UserCreate(UserBase):
    password: str = Field(
        min_length=10,
        examples=["aBcbde123*", "ABC^Dde1ab"],
        description="Password should have minimum 10 characters; at least 1 "
        "uppercase, 1 lowercase, 1 digit and 1 symbol in '#?! @$%^&*-'.",
    )
    pin: str = Field(min_length=10, max_length=10, pattern=r"[0-9A-Fa-f]+$")

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str):
        if (
            any(c.islower() for c in value)
            and any(c.isupper() for c in value)
            and any(c.isdigit() for c in value)
            and any(c in r"#?! @$%^&*-" for c in value)
        ):
            return value
        raise ValueError(
            "Password should have minimum 10 characters; at least 1 uppercase,"
            " 1 lowercase, 1 digit and 1 symbol in '#?! @$%^&*-'."
        )


class UserResponse(UserBase):
    user_id: int
    full_name: str

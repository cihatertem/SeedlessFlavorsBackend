# app/db/models.py

from typing import Annotated

from sqlalchemy import BIGINT, VARCHAR
from sqlalchemy.orm import mapped_column, Mapped

from .base import Base
from .mixins import TimeStampMixin, TableNameMixin

###########
# ANNOTATED
###########
int_primary_key = Annotated[
    int,
    mapped_column(BIGINT, primary_key=True, index=True),
]

str_text_with_20_chars = Annotated[
    str,
    mapped_column(VARCHAR(20), nullable=False),
]


###########
# MODELS
###########
class Category(Base, TimeStampMixin, TableNameMixin):
    category_id: Mapped[int_primary_key]
    name: Mapped[str] = mapped_column(VARCHAR(20), unique=True, nullable=False)


class User(Base, TimeStampMixin, TableNameMixin):
    user_id: Mapped[int_primary_key]
    first_name: Mapped[str_text_with_20_chars]
    last_name: Mapped[str_text_with_20_chars]
    email: Mapped[str] = mapped_column(
        VARCHAR(255), nullable=False, unique=True, index=True
    )
    username: Mapped[str] = mapped_column(
        VARCHAR(20), unique=True, nullable=False
    )
    password: Mapped[str] = mapped_column(VARCHAR(), nullable=False)

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

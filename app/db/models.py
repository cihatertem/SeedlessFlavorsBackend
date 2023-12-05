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
    mapped_column(BIGINT, primary_key=True),
]


###########
# MODELS
###########
class Category(Base, TimeStampMixin, TableNameMixin):
    category_id: Mapped[int_primary_key]
    name: Mapped[str] = mapped_column(VARCHAR(20), unique=True, nullable=False)

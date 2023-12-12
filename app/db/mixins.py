# app/db/mixins.py
import datetime

from sqlalchemy import func
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import declared_attr, Mapped, mapped_column


class TableNameMixin:
    @declared_attr.directive
    def __tablename__(cls):
        if cls.__name__.lower().endswith("y"):
            return cls.__name__.lower().removesuffix("y") + "ies"
        return cls.__name__.lower() + "s"


class TimeStampMixin:
    created_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP, server_default=func.now(), nullable=False
    )

    updated_at: Mapped[datetime.datetime | None] = mapped_column(
        TIMESTAMP,
        server_default=func.now(),
        onupdate=func.now(),
    )

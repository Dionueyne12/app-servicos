from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, func, text
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def new_uuid() -> UUID:
    return uuid4()


class Base(DeclarativeBase):
    pass


def uuid_pk_column():
    return mapped_column(
        PostgresUUID(as_uuid=True),
        primary_key=True,
        default=new_uuid,
        server_default=text("gen_random_uuid()"),
    )


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    created_by_usuario_id: Mapped[UUID | None] = mapped_column(PostgresUUID(as_uuid=True))
    updated_by_usuario_id: Mapped[UUID | None] = mapped_column(PostgresUUID(as_uuid=True))
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    deleted_by_usuario_id: Mapped[UUID | None] = mapped_column(PostgresUUID(as_uuid=True))


class CreatedAtMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

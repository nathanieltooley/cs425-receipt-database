from datetime import datetime, timezone
from warnings import warn
from typing import Sequence

from sqlalchemy import Column, ForeignKey, Table, TypeDecorator, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql.expression import func

UTC = timezone.utc


class Base(DeclarativeBase):
    """Used for actions regarding all tables"""

    pass


# https://docs.sqlalchemy.org/en/14/core/custom_types.html#store-timezone-aware-timestamps-as-timezone-naive-utc
class TZDateTime(TypeDecorator):
    impl = DateTime
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = value.astimezone(UTC).replace(tzinfo=None)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = value.replace(tzinfo=UTC)
        return value


"""Intermediary table for many-to-many relationship between receipts and tags"""
receipt_tag = Table(
    "receipt_tag",
    Base.metadata,
    Column("tag_id", ForeignKey("tag.id"), primary_key=True),
    Column("receipt_key", ForeignKey("receipt.id"), primary_key=True),
)


class Tag(Base):
    __tablename__ = "tag"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]

    def __eq__(self, other) -> bool:
        if not isinstance(other, Tag):
            return NotImplemented
        return self.id == other.id and self.name == other.name

    def export(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
        }


class Receipt(Base):
    __tablename__ = "receipt"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str | None] = mapped_column(default="Unnamed")
    storage_key: Mapped[str]
    upload_dt: Mapped[datetime] = mapped_column(
        type_=TZDateTime, server_default=func.now()
    )
    tags: Mapped[Sequence[Tag]] = relationship(
        secondary=receipt_tag, collection_class=list
    )

    def __eq__(self, other) -> bool:
        if not isinstance(other, Receipt):
            return NotImplemented
        return self.id == other.id and self.storage_key == other.storage_key

    def export(self) -> dict:
        if self.name == "":
            warn(f"Receipt.name is empty for {self.id = }")
        return {
            "id": self.id,
            "name": self.name,
            "storage_key": self.storage_key,
            "upload_dt": str(self.upload_dt),
            "tags": [t.id for t in self.tags],
        }

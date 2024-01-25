from datetime import datetime, UTC

from sqlalchemy import Column, ForeignKey, Table, TypeDecorator, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql.expression import func


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
    Column("receipt_key", ForeignKey("receipt.key"), primary_key=True),
)


class Tag(Base):
    __tablename__ = 'tag'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]


class Receipt(Base):
    __tablename__ = 'receipt'

    key: Mapped[str] = mapped_column(primary_key=True)
    body: Mapped[bytes]
    upload_dt: Mapped[datetime] = mapped_column(
        type_=TZDateTime, server_default=func.now()
    )
    tags: Mapped[list[Tag]] = relationship(secondary=receipt_tag)

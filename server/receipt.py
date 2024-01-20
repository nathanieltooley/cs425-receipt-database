from datetime import datetime, UTC

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql.expression import func


class Base(DeclarativeBase):
    """Used for actions regarding all tables"""
    pass


class Receipt(Base):
    __tablename__ = 'receipt'

    key: Mapped[str] = mapped_column(primary_key=True)
    body: Mapped[bytes]
    _upload_dt: Mapped[datetime] = mapped_column(server_default=func.now())

    @property
    def upload_dt(self) -> datetime:
        if self._upload_dt.tzinfo is None:  # Set to UTC if no timezone set
            self._upload_dt = self.upload_dt.astimezone(UTC)
        return self._upload_dt

    @upload_dt.setter
    def upload_dt(self, dt: datetime):
        if not isinstance(dt, datetime):
            raise ValueError(f'upload_dt must be datetime.datetime, got {type(dt)}')
        self._upload_dt = dt.astimezone(UTC)  # Sets or converts to UTC datetime

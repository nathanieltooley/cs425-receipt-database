import abc
import datetime as dt
import enum
from pathlib import Path

from sqlalchemy import Engine, select, delete, asc, desc
from sqlalchemy.orm import Session, selectinload

from receipt import Receipt, Base, Tag
from typing import Optional, Sequence, Iterable

UTC = dt.timezone.utc


class ReceiptSort(enum.Enum):
    """Represents different methods to sort data."""

    newest = desc(Receipt.upload_dt)  # Newer items before older, a.k.a newest first
    oldest = asc(Receipt.upload_dt)  # Older items before newer, a.k.a oldest first


class DatabaseHook(abc.ABC):
    storage_version = "0.2.0"

    def __init__(self):
        self.engine: Engine = NotImplemented

    def save_objects(self, *objects: Base):
        with Session(self.engine) as session:
            session.add_all(objects)
            session.commit()

    def delete_objects(self, *objects: Base):
        with Session(self.engine) as session:
            for obj in objects:
                session.delete(obj)
            session.commit()

    def create_receipt(self, receipt: Receipt) -> Receipt:
        with Session(self.engine) as session:
            session.add(receipt)
            session.commit()
            full_receipt = self.fetch_receipt(receipt.id)
            if full_receipt is None:
                raise RuntimeError
            return full_receipt

    def fetch_receipt(self, id_: int) -> Optional[Receipt]:
        stmt = (
            select(Receipt).options(selectinload(Receipt.tags)).where(Receipt.id == id_)
        )
        with Session(self.engine) as session:
            return session.scalar(stmt)

    def fetch_receipts(
        self,
        after: Optional[dt.datetime] = None,
        before: Optional[dt.datetime] = None,
        tags: Optional[list[Tag]] = None,
        match_all_tags: bool = False,
        limit: Optional[int] = None,
        sort: ReceiptSort = ReceiptSort.newest,
    ) -> Sequence[Receipt]:
        stmt = select(Receipt).options(selectinload(Receipt.tags)).order_by(sort.value)
        if after is not None:
            stmt = stmt.where(after < Receipt.upload_dt)
        if before is not None:
            stmt = stmt.where(before > Receipt.upload_dt)
        if tags is not None:
            if match_all_tags:
                stmt = stmt.where(Receipt.tags.all(Tag.id.in_(tags)))
            else:
                stmt = stmt.where(Receipt.tags.any(Tag.id.in_(tags)))
        if limit is not None:
            stmt = stmt.limit(limit)

        with Session(self.engine) as session:
            return session.scalars(stmt).all()

    def update_receipt(
        self,
        receipt_id: int,
        name: str | None = None,
        set_tags: Iterable[int] | None = None,
        add_tags: Iterable[int] | None = None,
        remove_tags: Iterable[int] | None = None,
    ) -> Receipt:
        with Session(self.engine) as session:
            receipt = session.get_one(Receipt, receipt_id)
            if name is not None:
                receipt.name = name

            if set_tags is not None:
                tag_ids = set_tags
            else:
                tag_ids = [tag.id for tag in receipt.tags]
            tag_ids = set(tag_ids)
            if add_tags is not None:
                tag_ids.update(add_tags)
            if remove_tags is not None:
                tag_ids.difference_update(remove_tags)

            receipt.tags = session.scalars(
                select(Tag).filter(Tag.id.in_(tag_ids))
            ).all()

            session.commit()
        return self.fetch_receipt(receipt_id)

    def delete_receipt(self, id_: int):
        with Session(self.engine) as session:
            stmt = delete(Receipt).where(
                Receipt.id == id_
            )  # .returning(Receipt.storage_key)
            # key = session.execute(stmt).one()[0]
            session.execute(stmt)
            session.commit()
            # return key

    def create_tag(self, tag: Tag) -> Tag:
        with Session(self.engine) as session:
            session.add(tag)
            session.commit()
            full_tag = self.fetch_tag(tag.id)
            if full_tag is None:
                raise RuntimeError
            return full_tag

    def fetch_tag(self, tag_id: int) -> Optional[Tag]:
        stmt = select(Tag).where(Tag.id == tag_id)
        with Session(self.engine) as session:
            return session.scalar(stmt)

    def fetch_tags(self, tag_ids: Optional[list[int]] = None) -> Sequence[Tag]:
        with Session(self.engine) as session:
            stmt = select(Tag)
            if tag_ids is not None:
                stmt = stmt.filter(Tag.id.in_(tag_ids))
            return session.scalars(stmt).all()

    def update_tag(self, updated_tag: Tag) -> Tag:
        return self.create_tag(updated_tag)

    def delete_tag(self, tag_id: int) -> None:
        with Session(self.engine) as session:
            stmt = delete(Tag).where(Tag.id == tag_id)
            session.execute(stmt)
            session.commit()

    def initialize_storage(self, clean: bool = True):
        """Initialize storage / database with current scheme.

        Args:
            clean: Delete any existing data that may be present
        """
        if clean:
            Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)


class FileHook(abc.ABC):
    """Base class for hooks that store image files."""

    @staticmethod
    def _make_key(original_name: str):
        filename = Path(original_name)
        now = dt.datetime.now(UTC).isoformat(timespec="seconds")
        return f"{filename.stem} ({now}){filename.suffix}"

    @abc.abstractmethod
    def save(self, image: bytes, original_name: str) -> str:
        """Saves an image

        Args:
            image: The bytes to save as an image
            original_name: Filename of the uploaded image to generate a key from
        Returns:
            The string location to fetch the image later
        """

    @abc.abstractmethod
    def replace(self, location: str, image: bytes):
        """Replace image at location with new image

        Args:
            location: The location of the image to replace
            image: The image to replace with

        Raises:
            FileNotFoundError: When the location doesn't exist
        """

    @abc.abstractmethod
    def fetch(self, location: str) -> bytes:
        """Fetches image from location as bytes

        Args:
            location: Location of the image to fetch

        Returns:
            byte representation of the image

        Raises:
            FileNotFoundError: When the location doesn't exist
        """

    @abc.abstractmethod
    def delete(self, location: str):
        """Deletes the image at location

        Args:
            location: Location of the image to delete

        Raises:
            FileNotFoundError: When the location doesn't exist
        """

    @abc.abstractmethod
    def initialize_storage(self, clean: bool = False):
        """Perform hook one time setup steps

        Args:
            clean: Delete any existing data that may be present
        """

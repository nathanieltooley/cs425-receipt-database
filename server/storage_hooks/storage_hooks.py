import abc
import datetime as dt
import enum
from pathlib import Path
from typing import Iterable, Optional, Sequence

from sqlalchemy import Engine, asc, delete, desc, select
from sqlalchemy.orm import Session, selectinload

from receipt import Base, Receipt, Tag

UTC = dt.timezone.utc


class ReceiptSort(enum.Enum):
    """Represents different methods to sort data."""

    newest = desc(Receipt.upload_dt)  # Newer items before older, a.k.a newest first
    oldest = asc(Receipt.upload_dt)  # Older items before newer, a.k.a oldest first


class DatabaseHook(abc.ABC):
    storage_version = "0.2.0"

    def __init__(self):
        self.engine: Engine = NotImplemented

    def save_objects(self, *objects: Base) -> None:
        """Save all provided object metadata

        (No uses)
        Args:
            *objects: objects to be saved

        Returns:
            Nothing
        """
        with Session(self.engine) as session:
            session.add_all(objects)
            session.commit()

    def delete_objects(self, *objects: Base) -> None:
        """Delete all provided object metadata

        (Only uses in tests and subclasses)
        Args:
            *objects: objects to delete

        Returns:
            Nothing
        """
        with Session(self.engine) as session:
            for obj in objects:
                session.delete(obj)
            session.commit()

    def create_receipt(self, receipt: Receipt) -> Receipt:
        """Save a new receipt to the database

        Notes:
            Expected to generate the `receipt.id`

        Args:
            receipt: The receipt to save

        Returns:
            The receipt, updated with an id
        """
        with Session(self.engine) as session:
            session.add(receipt)
            session.commit()
            full_receipt = self.fetch_receipt(receipt.id)
            if full_receipt is None:
                raise RuntimeError
            return full_receipt

    def fetch_receipt(self, id_: int) -> Optional[Receipt]:
        """Retrieve a receipt from the database

        Args:
            id_: The id of the receipt to retrieve

        Returns:
            The retrieved receipt if it exists, None otherwise.
        """
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
        """Retrieve multiple receipts from the database

        Args:
            after: Only include receipts with an upload_dt after _
            before: Only include receipts with an upload_dt before _
            tags: Only include receipts with _ tags
            match_all_tags:
                True: Require receipts to have *all* tags
                False: Require receipts to have *any* of the tags
            limit: Maximum number of results to return
            sort: Method to sort results (applies before limit)

        Returns:
            A sequence of receipts that match the parameters.
        """
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
        """Update an existing receipt

        Args:
            receipt_id: The id of the receipt to update
            name: The new name to give to the receipt
            set_tags: Tags to apply to the receipt. Removes any not included.
            add_tags: Tags to add to the receipt. Applies after set_tags.
            remove_tags: Tags to remove from the receipt. Applies after add_tags.

        Returns:
            The Receipt with updated values.
        """
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

    def delete_receipt(self, id_: int) -> None:
        """Delete receipt from the database

        Args:
            id_: The id of the receipt to delete

        Returns:
            Nothing
        """
        with Session(self.engine) as session:
            stmt = delete(Receipt).where(
                Receipt.id == id_
            )  # .returning(Receipt.storage_key)
            # key = session.execute(stmt).one()[0]
            session.execute(stmt)
            session.commit()
            # return key

    def create_tag(self, tag: Tag) -> Tag:
        """Save a tag to the database

        Notes:
            Expected to generate the `tag.id`

        Args:
            tag: The tag to save

        Returns:
            The tag, updated with an id
        """
        with Session(self.engine) as session:
            session.add(tag)
            session.commit()
            full_tag = self.fetch_tag(tag.id)
            if full_tag is None:
                raise RuntimeError
            return full_tag

    def fetch_tag(self, tag_id: int) -> Optional[Tag]:
        """Retrieve a tag from the database

        Args:
            tag_id: The id of the tag to retrieve

        Returns:
            The retrieved tag if it exists, None otherwise.
        """
        stmt = select(Tag).where(Tag.id == tag_id)
        with Session(self.engine) as session:
            return session.scalar(stmt)

    def fetch_tags(self, tag_ids: Optional[list[int]] = None) -> Sequence[Tag]:
        """Retrieve multiple tags from the database

        Args:
            tag_ids: List of ids of tags to exclusively include

        Returns:
            A sequence of all (or filtered by tag_ids) tags.
        """
        with Session(self.engine) as session:
            stmt = select(Tag)
            if tag_ids is not None:
                stmt = stmt.filter(Tag.id.in_(tag_ids))
            return session.scalars(stmt).all()

    def update_tag(self, updated_tag: Tag) -> Tag:
        """Update an existing tag

        Args:
            updated_tag: The tag with updated values.

        Returns:
            The Tag with updated values.
        """
        return self.create_tag(updated_tag)

    def delete_tag(self, tag_id: int) -> None:
        """Delete tag from the database

        Args:
            tag_id: The id of the tag to delete

        Returns:
            Nothing
        """
        with Session(self.engine) as session:
            stmt = delete(Tag).where(Tag.id == tag_id)
            session.execute(stmt)
            session.commit()

    def initialize_storage(self, clean: bool = True) -> None:
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
    def _make_key(original_name: str) -> str:
        """Makes a (hopefully) unique filename for saving"""
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
    def replace(self, location: str, image: bytes) -> None:
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
    def delete(self, location: str) -> None:
        """Deletes the image at location

        Args:
            location: Location of the image to delete

        Raises:
            FileNotFoundError: When the location doesn't exist
        """

    @abc.abstractmethod
    def initialize_storage(self, clean: bool = False) -> None:
        """Perform hook one time setup steps

        Args:
            clean: Delete any existing data that may be present
        """

import abc
import datetime as dt
import enum
from pathlib import Path

from sqlalchemy import Engine, select, delete, asc, desc
from sqlalchemy.orm import Session, selectinload

from receipt import Receipt, Base, Tag

UTC = dt.timezone.utc


class ReceiptSort(enum.Enum):
    """Represents different methods to sort data."""

    newest = desc(Receipt.upload_dt)  # Newer items before older, a.k.a newest first
    oldest = asc(Receipt.upload_dt)  # Older items before newer, a.k.a oldest first


class DatabaseHook(abc.ABC):
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

    def create_receipt(self, receipt: Receipt) -> int:
        with Session(self.engine) as session:
            session.add(receipt)
            session.commit()
            return receipt.id

    def fetch_receipt(self, id_: int) -> Receipt:
        stmt = select(Receipt).where(Receipt.id == id_)
        with Session(self.engine) as session:
            return session.scalar(stmt)

    def fetch_receipts(
        self,
        after: dt.datetime = None,
        before: dt.datetime = None,
        tags: list[Tag] = None,
        match_all_tags: bool = False,
        limit: int = None,
        sort: ReceiptSort = ReceiptSort.newest,
    ) -> list[Receipt]:
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

    def update_receipt(self, diff: dict) -> Receipt:
        raise NotImplementedError

    def delete_receipt(self, id_: Receipt.id) -> str:
        with Session(self.engine) as session:
            stmt = (
                delete(Receipt).where(Receipt.id == id_).returning(Receipt.storage_key)
            )
            return session.execute(stmt).one()[0]

    def create_tag(self, tag: Tag) -> int:
        with Session(self.engine) as session:
            session.add(tag)
            session.commit()
            return tag.id

    def fetch_tag(self, tag_id: int) -> Tag:
        stmt = select(Tag).where(Tag.id == tag_id)
        with Session(self.engine) as session:
            return session.scalar(stmt)

    def fetch_tags(self, tag_ids: list[int] = None) -> list[Tag]:
        with Session(self.engine) as session:
            stmt = select(Tag)
            if tag_ids is not None:
                stmt = stmt.filter(Tag.id.in_(tag_ids))
            return session.scalars(stmt).all()

    def update_tag(self, diff: dict) -> Tag:
        raise NotImplementedError

    def delete_tag(self, tag_id: Tag.id) -> None:
        with Session(self.engine) as session:
            stmt = delete(Tag).where(Tag.id == tag_id)
            session.execute(stmt)

    @property
    @abc.abstractmethod
    def storage_version(self) -> str:
        """Return scheme version the database is using."""

    def initialize_storage(self):
        """Initialize storage / database with current scheme."""
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


class StorageHook(abc.ABC):
    """Base class for hooks to specific services to utilize."""

    def __init__(self):
        pass

    @abc.abstractmethod
    def upload_receipt(self, receipt: Receipt) -> bool:
        """Upload a receipt to storage.

        Args:
            receipt: The receipt to upload.

        Returns:
            True if successful, False otherwise.
        """
        pass

    @abc.abstractmethod
    def fetch_receipt(self, identifier) -> Receipt:
        """Fetch a receipt from storage.

        Args:
            identifier: The identifier of the receipt to fetch.

        Returns:
            The receipt fetched from storage.
        """
        pass

    @abc.abstractmethod
    def fetch_receipts(
        self, limit: int = None, sort: ReceiptSort = ReceiptSort.newest
    ) -> list[Receipt]:
        """Fetch multiple receipts from storage.

        Args:
            limit: The maximum number of receipts to fetch. Applied after sorting.
            sort: The method for sorting the receipts.

        Returns:
            A list of the fetched receipts.
        """
        pass

    @abc.abstractmethod
    def fetch_receipts_between(
        self,
        after: dt.datetime,
        before: dt.datetime,
        limit: int = None,
        sort: ReceiptSort = ReceiptSort.newest,
    ) -> list[Receipt]:
        """Fetch receipts dated between `before` and `after` from storage.

        Args:
            after: The minimum datetime of receipts to fetch.
            before: The maximum datetime of receipts to fetch.
            limit: The maximum number of receipts to fetch. Applied after sorting.
            sort: The method for sorting the receipts.

        Returns:
            A list of the fetched receipts.
        """
        pass

    @abc.abstractmethod
    def edit_receipt(self, receipt: Receipt) -> bool:
        """Edit a receipt in storage.

        Args:
            receipt: The receipt to edit.

        Returns:
            True if successful, False otherwise.
        """
        pass

    @abc.abstractmethod
    def delete_receipt(self, receipt) -> bool:
        """Delete a receipt from storage.

        Args:
            receipt: The receipt to delete.

        Returns:
            True if successful, False otherwise.
        """
        pass

    def delete_receipt_by_id(self, identifier) -> bool:
        """Delete a receipt from storage.

        Args:
            identifier: The identifier of the receipt to delete.

        Returns:
            True if successful, False otherwise.
        """
        receipt = self.fetch_receipt(identifier)
        return self.delete_receipt(receipt)

    def migrate_to_service(self, new_service: "StorageHook") -> bool:
        """Migrate all currently stored receipts to a new service.

        Args:
            new_service: The StorageHook for the service to migrate to.

        Returns:
            True if successful, False otherwise.
        """
        for receipt in self.fetch_receipts():
            if not new_service.upload_receipt(receipt):
                return False
        return True

    @property
    @abc.abstractmethod
    def storage_version(self) -> str:
        """Return scheme version the database is using."""

    @abc.abstractmethod
    def initialize_storage(self):
        """Initialize storage / database with current scheme."""

    @abc.abstractmethod
    def update_storage(self) -> bool:
        """Migrates a copy of the database to the current scheme version.

        Returns:
            True if successful, False otherwise.
        """
        pass

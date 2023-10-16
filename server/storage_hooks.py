import abc
import datetime as dt
import enum

from receipt import Receipt


class Sort(enum.Enum):
    """Represents different methods to sort data."""

    newest = enum.auto()  # Newer items before older, a.k.a newest first
    oldest = enum.auto()  # Older items before newer, a.k.a oldest first


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
        self, limit: int = None, sort: Sort = Sort.newest
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
        sort: Sort = Sort.newest,
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

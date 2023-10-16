import abc
import datetime as dt
import enum

from receipt import Receipt


class Sort(enum.Enum):
    """Represents different methods to sort data."""
    newest = enum.auto()  # Newer items before older, a.k.a newest first
    oldest = enum.auto()  # Older items before newer, a.k.a oldest first


class StorageHook(abc.ABC):
    def __init__(self):
        pass

    @abc.abstractmethod
    def upload_receipt(self, receipt: Receipt) -> bool:
        pass

    @abc.abstractmethod
    def fetch_receipt(self, identifier) -> Receipt:
        pass

    @abc.abstractmethod
    def fetch_receipts(
        self, limit: int = None, sort: Sort = Sort.newest
    ) -> list[Receipt]:
        pass

    @abc.abstractmethod
    def fetch_receipts_between(
        self,
        before: dt.datetime,
        after: dt.datetime,
        limit: int = None,
        sort: Sort = Sort.newest,
    ) -> list[Receipt]:
        pass

    @abc.abstractmethod
    def edit_receipt(self, receipt: Receipt) -> bool:
        pass

    @abc.abstractmethod
    def delete_receipt(self, receipt) -> bool:
        pass

    def delete_receipt_by_id(self, identifier) -> bool:
        receipt = self.fetch_receipt(identifier)
        return self.delete_receipt(receipt)

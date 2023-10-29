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

    @abc.abstractmethod
    @property
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


class AWSHook(StorageHook):
    """Connection to AWS Storage"""

    def __init__(self):
        import boto3

        super().__init__()
        self.client = boto3.client("s3")
        # ToDo: Configurable Bucket Name
        self.bucket_name = "cs425-3-test-bucket"

    def upload_receipt(self, receipt: Receipt) -> bool:
        r = self.client.put_object(
            Bucket=self.bucket_name, Key=receipt.ph_key, Body=receipt.ph_body
        )
        return r == 200

    def fetch_receipt(self, identifier) -> Receipt:
        try:
            data = (
                self.client.get_object(Bucket=self.bucket_name, Key=identifier)
                .get("Body")
                .read()
            )
            # data['ResponseMetadata']['HTTPStatusCode'] should equal 200
            return Receipt(identifier, data)
        except AttributeError:
            raise ValueError

    def fetch_receipts(
        self, limit: int = None, sort: Sort = Sort.newest
    ) -> list[Receipt]:
        pass

    def fetch_receipts_between(
        self,
        after: dt.datetime,
        before: dt.datetime,
        limit: int = None,
        sort: Sort = Sort.newest,
    ) -> list[Receipt]:
        pass

    def edit_receipt(self, receipt: Receipt) -> bool:
        return self.upload_receipt(receipt)

    def delete_receipt(self, receipt) -> bool:
        r = self.client.delete_object(Bucket=self.bucket_name, Key=receipt.ph_key)
        return r["ResponseMetadata"]["HTTPStatusCode"] == 204

    @property
    def storage_version(self) -> str:
        """Return scheme version the database is using."""
        return "0.1.0"

    def initialize_storage(self):
        """Initialize storage / database with current scheme."""
        import warnings
        import botocore.exceptions

        try:
            _r = self.client.create_bucket(Bucket=self.bucket_name)
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "BucketAlreadyExists":
                raise ValueError(f"Bucket {self.bucket_name} Already Exists")
            elif e.response["Error"]["Code"] == "BucketAlreadyOwnedByYou":
                warnings.warn(f"You already own Bucket {self.bucket_name}")
            else:
                raise

    def update_storage(self) -> bool:
        """Migrates a copy of the database to the current scheme version.

        Returns:
            True if successful, False otherwise.
        """
        return True

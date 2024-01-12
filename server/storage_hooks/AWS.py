import datetime as dt
import warnings

import boto3
import botocore.exceptions

from receipt import Receipt
from storage_hooks.storage_hooks import StorageHook, Sort


def init_script():
    """Script to initialize AWSHook."""
    # ToDo: Configure AWS Hook locally. I.e. use a `botocore.config.Config`
    # another option would to be internally set the environment variables boto3 uses
    import subprocess

    subprocess.run(["aws", "configure"])
    hook = AWSHook()
    hook.initialize_storage()


class AWSHook(StorageHook):
    """Connection to AWS Storage"""

    def __init__(self):
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

        try:
            _r = self.client.create_bucket(Bucket=self.bucket_name)
        except botocore.exceptions.ClientError as e:
            match e.response["Error"]["Code"]:
                case "BucketAlreadyExists":
                    raise ValueError(f"Bucket {self.bucket_name} Already Exists")
                case "BucketAlreadyOwnedByYou":
                    warnings.warn(f"You already own Bucket {self.bucket_name}")
                case e_ec if e_ec in [
                    "IllegalLocationConstraintException",
                    "InvalidLocationConstraint",
                ]:
                    # This case seems undocumented
                    # When client on us-east-1 and bucket.name = "cs425-3-test-bucket",
                    # it raises IllegalLocationConstraintException, even if given a
                    # CreateBucketConfiguration={"LocationConstraint": <region>}.
                    # When client on us-east-1 and bucket.name = "cs425-3-test-bucket2",
                    # it raises InvalidLocationConstraint when only when given a
                    # CreateBucketConfiguration={"LocationConstraint": <region>}.
                    raise
                case _:
                    raise

    def update_storage(self) -> bool:
        """Migrates a copy of the database to the current scheme version.

        Returns:
            True if successful, False otherwise.
        """
        return True

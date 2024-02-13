import datetime as dt
import warnings

import boto3
import botocore.exceptions

from receipt import Receipt
from storage_hooks.storage_hooks import StorageHook, ReceiptSort, FileHook


def init_script():
    """Script to initialize AWSHook."""
    # ToDo: Configure AWS Hook locally. I.e. use a `botocore.config.Config`
    # another option would to be internally set the environment variables boto3 uses
    import subprocess

    subprocess.run(["aws", "configure"])
    hook = AWSS3Hook()
    hook.initialize_storage()


class AWSS3Hook(FileHook):
    """Connection to AWS Storage"""

    def __init__(self):
        super().__init__()
        self.client = boto3.client("s3")
        # ToDo: Configurable Bucket Name
        self.bucket_name = "cs425-3-test-bucket"

    def save(self, image: bytes, original_name: str) -> str:
        key = self._make_key(original_name)
        r = self.client.put_object(
            Bucket=self.bucket_name,
            Key=key,
            Body=image,
        )
        if r["ResponseMetadata"]["HTTPStatusCode"] != 200:
            raise RuntimeError(
                f"S3 return code {r['ResponseMetadata']['HTTPStatusCode']} != 200"
            )
        return key

    def fetch(self, location: str) -> bytes:
        try:
            obj = self.client.get_object(Bucket=self.bucket_name, Key=location)
            # data['ResponseMetadata']['HTTPStatusCode'] should equal 200
            return obj.get("Body").read()
        except AttributeError:
            raise ValueError

    def replace(self, location: str, image: bytes):
        # ToDo: Check location exists
        r = self.client.put_object(
            Bucket=self.bucket_name,
            Key=location,
            Body=image,
        )
        if not r == 200:
            raise RuntimeError(f"S3 return code {r} != 200")

    def delete(self, location: str):
        r = self.client.delete_object(Bucket=self.bucket_name, Key=location)
        if (r_code := r["ResponseMetadata"]["HTTPStatusCode"]) != 204:
            raise RuntimeError(f"S3 return code {r_code} != 204")

    def initialize_storage(self):
        """Initialize storage / database with current scheme."""

        # try:
        _r = self.client.create_bucket(Bucket=self.bucket_name)
        # except botocore.exceptions.ClientError as e:
        #     match e.response["Error"]["Code"]:
        #         case "BucketAlreadyExists":
        #             raise ValueError(f"Bucket {self.bucket_name} Already Exists")
        #         case "BucketAlreadyOwnedByYou":
        #             warnings.warn(f"You already own Bucket {self.bucket_name}")
        #         case e_ec if e_ec in [
        #             "IllegalLocationConstraintException",
        #             "InvalidLocationConstraint",
        #         ]:
        #             # This case seems undocumented
        #             # When client on us-east-1 and bucket.name = "cs425-3-test-bucket",
        #             # it raises IllegalLocationConstraintException, even if given a
        #             # CreateBucketConfiguration={"LocationConstraint": <region>}.
        #             # When client on us-east-1 and bucket.name = "cs425-3-test-bucket2",
        #             # it raises InvalidLocationConstraint when only when given a
        #             # CreateBucketConfiguration={"LocationConstraint": <region>}.
        #             raise
        #         case _:
        #             raise

    def update_storage(self) -> bool:
        """Migrates a copy of the database to the current scheme version.

        Returns:
            True if successful, False otherwise.
        """
        return True

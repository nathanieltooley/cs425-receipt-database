import warnings

import boto3
import botocore.exceptions
from botocore import logging

from configure import CONFIG
from storage_hooks.storage_hooks import FileHook


class AWSS3Hook(FileHook):
    """Connection to AWS Storage"""

    def __init__(self):
        super().__init__()
        self.config = CONFIG.AWSS3

        self.client = boto3.client(
            "s3",
            aws_access_key_id=self.config.access_key_id,  # Key as str or None
            aws_secret_access_key=self.config.secret_access_key,  # Ditto
        )
        self.bucket_name = self.config.bucket_name

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
        print(location)
        try:
            obj = self.client.get_object(Bucket=self.bucket_name, Key=location)
            # data['ResponseMetadata']['HTTPStatusCode'] should equal 200
            return obj.get("Body").read()
        except AttributeError:
            raise ValueError
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                raise FileNotFoundError
            raise

    def replace(self, location: str, image: bytes):
        try:
            self.client.head_object(Bucket=self.bucket_name, Key=location)
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "404":
                raise FileNotFoundError
            raise

        r = self.client.put_object(
            Bucket=self.bucket_name,
            Key=location,
            Body=image,
        )
        if r["ResponseMetadata"]["HTTPStatusCode"] != 200:
            raise RuntimeError(f"S3 return code {r} != 200")

    def delete(self, location: str):
        try:
            self.client.head_object(Bucket=self.bucket_name, Key=location)
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "404":
                raise FileNotFoundError
            raise

        try:
            r = self.client.delete_object(Bucket=self.bucket_name, Key=location)
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                raise FileNotFoundError
            else:
                raise RuntimeError
        if (r_code := r["ResponseMetadata"]["HTTPStatusCode"]) != 204:
            raise RuntimeError(f"S3 return code {r_code} != 204")

    def _delete_all(self):
        """Deletes all objects from the bucket"""
        objects = self.client.list_objects_v2(Bucket=self.bucket_name)

        try:
            if objects["Contents"] is not None:
                formatted = [{"Key": obj["Key"]} for obj in objects["Contents"]]
                self.client.delete_objects(
                    Bucket=self.bucket_name, Delete={"Objects": formatted}
                )
        except KeyError:
            logging.warning("AWS Storage Hook attempted to delete an empty bucket")

    def initialize_storage(self, clean: bool = False):
        """Initialize storage / database with current scheme."""
        try:
            _r = self.client.head_bucket(Bucket=self.bucket_name)
        except botocore.exceptions.ClientError as e:
            match e.response["Error"]["Code"]:
                case 403:
                    raise ValueError(f"Bucket {self.bucket_name} Already Exists")
                case 404:
                    pass
                case _:
                    raise
        else:
            if clean:
                self._delete_all()
            return
        try:
            _r = self.client.create_bucket(Bucket=self.bucket_name)
        except botocore.exceptions.ClientError as e:
            match e.response["Error"]["Code"]:
                case "BucketAlreadyExists":
                    raise ValueError(f"Bucket {self.bucket_name} Already Exists")
                case "BucketAlreadyOwnedByYou":
                    warnings.warn(
                        f"Bucket {self.bucket_name} already exists and is owned by you"
                    )
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

import boto3
import os


class Client:
    MINIO_ENDPOINT = os.environ.get("MINIO_ENDPOINT", "http://localhost:9000")
    MINIO_ACCESS_KEY = os.environ.get("MINIO_ACCESS_KEY", "minioadmin")
    MINIO_SECRET_KEY = os.environ.get("MINIO_SECRET_KEY", "minioadmin")

    def __init__(self):
        self.client = boto3.resource(
            "s3",
            endpoint_url=self.MINIO_ENDPOINT,
            asw_access_key_id=self.MINIO_ACCESS_KEY,
            aws_secret_access_key=self.MINIO_SECRET_KEY,
            aws_session_token=None,
            config=boto3.session.Config(signature_version="s3v4"),
        )

    def download_file(self, local_path, key, bucket_name):
        self.client.Bucket(bucket_name).download_file(key, local_path)
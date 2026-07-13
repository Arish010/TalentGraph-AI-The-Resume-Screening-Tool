import os
import boto3
from botocore.exceptions import ClientError

class S3Service:
    def __init__(self, bucket_name: str):
        self.bucket_name = bucket_name
        # Initialize the S3 client using environment variables
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_DEFAULT_REGION", "eu-west-2")
        )

    def download_file_to_string(self, file_key: str) -> str:
        """Downloads a text file from S3 directly into a Python string."""
        try:
            print(f"[AWS S3] Downloading {file_key} from bucket '{self.bucket_name}'...")
            response = self.s3.get_object(Bucket=self.bucket_name, Key=file_key)
            return response['Body'].read().decode('utf-8')
        except ClientError as e:
            print(f"[AWS S3 ERROR] Failed to download {file_key}: {e}")
            raise e

    def list_resume_keys(self, prefix: str = "resumes/") -> list:
        """Lists all files in the bucket under a specific folder prefix."""
        try:
            response = self.s3.list_objects_v2(Bucket=self.bucket_name, Prefix=prefix)
            keys = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    # Only grab actual files, ignore the folder directory placeholder itself
                    if not obj['Key'].endswith('/'):
                        keys.append(obj['Key'])
            return keys
        except ClientError as e:
            print(f"[AWS S3 ERROR] Failed to list files: {e}")
            return []   
    
    def upload_file_bytes(self, file_bytes: bytes, file_key: str) -> bool:
        """Uploads raw file bytes directly to the S3 bucket."""
        try:
            print(f"[AWS S3] Uploading {file_key} to bucket '{self.bucket_name}'...")
            self.s3.put_object(Bucket=self.bucket_name, Key=file_key, Body=file_bytes)
            return True
        except ClientError as e:
            print(f"[AWS S3 ERROR] Upload failed: {e}")
            return False
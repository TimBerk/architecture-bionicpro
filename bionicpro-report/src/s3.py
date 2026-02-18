import datetime
from minio import Minio
from minio.error import S3Error
from src.config import settings


def get_s3() -> Minio:
    return Minio(
        endpoint=settings.S3_ENDPOINT,
        access_key=settings.S3_ACCESS_KEY,
        secret_key=settings.S3_SECRET_KEY,
        secure=settings.S3_SECURE == "1",
    )


def cdn_url(bucket: str, key: str) -> str:
    return f"{settings.CDN_BASE_URL.rstrip('/')}/reports/{bucket}/{key}"


def report_key(email: str) -> str:
    return f"reports/user/email={email}/latest.pdf"

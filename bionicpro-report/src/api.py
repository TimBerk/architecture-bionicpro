import io
from fastapi import APIRouter, HTTPException, Depends, Response

from src.models import UserReport
from src.clients import ch_client
from src.s3 import get_s3, cdn_url, report_key
from minio import S3Error
from src.config import settings
from src.di import get_current_user
from src.builder import build_report


router = APIRouter()


@router.get("/api/reports")
def get_report(user=Depends(get_current_user)):
    bucket = settings.S3_BUCKET
    key = report_key(user.email)
    client = get_s3()

    try:
        client.stat_object(bucket, key)
        return {"url": cdn_url(bucket, key)}
    except S3Error as e:
        if e.code not in ("NoSuchKey", "NoSuchObject", "NotFound"):
            raise

    ch = ch_client()
    q = f"""
            SELECT
              c.email,
              c.country,
              count(p.prosthesis_id) AS prosthesis_total,
              sum(p.is_active) AS prosthesis_active,
              greatest(c.updated_at, max(p.updated_at)) AS updated_at
            FROM reports.crm_clients_dim AS c
            LEFT JOIN reports.crm_client_prosthesis_dim AS p ON p.email = c.email
            WHERE c.email = '{user.email}'
            GROUP BY c.email, c.country, c.updated_at
        """
    res = ch.query(q)
    if not res.result_rows:
        raise HTTPException(status_code=404, detail="Report not found")

    row = res.result_rows[0]
    report = UserReport(
        email=row[0],
        country=row[1],
        prosthesis_total=int(row[2]),
        prosthesis_active=int(row[3]),
        updated_at=row[4],
    ).model_dump()

    pdf_bytes = build_report(report)

    client.put_object(
        bucket_name=bucket,
        object_name=key,
        data=io.BytesIO(pdf_bytes),
        length=len(pdf_bytes),
        content_type="application/pdf",
    )

    return {"url": cdn_url(bucket, key)}

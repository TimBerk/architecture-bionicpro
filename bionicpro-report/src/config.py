from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    AUTH_BASE_URL: str = "http://bionicpro-auth:8001"
    AUTH_COOKIE_NAME: str = "sid"  # должен совпадать с s.cookie_name в auth

    # ClickHouse
    CH_HOST: str = "clickhouse"
    CH_PORT: int = 8123
    CH_DB: str = "reports"
    CH_USER: str | None = None
    CH_PASSWORD: str | None = None
    CH_CONNECT_TIMEOUT: float = 5
    CH_SEND_RECEIVE_TIMEOUT: float = 30

    # MinIO
    S3_BUCKET: str | None = None
    S3_ENDPOINT: str | None = None
    S3_ACCESS_KEY: str | None = None
    S3_SECRET_KEY: str | None = None
    S3_SECURE: str | None = None
    CDN_BASE_URL: str | None = None


settings = Settings()

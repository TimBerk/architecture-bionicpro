import clickhouse_connect

from src.config import settings


def ch_client():
    return clickhouse_connect.get_client(
        host=settings.CH_HOST,
        port=settings.CH_PORT,
        username=settings.CH_USER,
        password=settings.CH_PASSWORD,
        database=settings.CH_DB,
        connect_timeout=settings.CH_CONNECT_TIMEOUT,
        send_receive_timeout=settings.CH_SEND_RECEIVE_TIMEOUT,
    )

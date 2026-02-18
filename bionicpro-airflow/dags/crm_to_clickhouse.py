from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

import clickhouse_connect
from airflow import DAG
from airflow.hooks.base import BaseHook
from airflow.models import Variable
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook


log = logging.getLogger(__name__)

DAG_ID = "crm_to_clickhouse_incremental"
SCHEDULE = "0 2 * * *"

CRM_CONN_ID = "crm_pg"
CH_CONN_ID = "clickhouse_reports"
WATERMARK_VAR = "crm_etl_last_loaded_at"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def get_watermark() -> str:
    return Variable.get(WATERMARK_VAR, default_var="1970-01-01T00:00:00+00:00")


def set_watermark(value: str) -> None:
    Variable.set(WATERMARK_VAR, value)


def get_clickhouse_client():
    conn = BaseHook.get_connection(CH_CONN_ID)
    extra = conn.extra_dejson or {}

    return clickhouse_connect.get_client(
        host=conn.host,
        port=conn.port or 8123,
        username=conn.login or None,
        password=conn.password or None,
        database=conn.schema or extra.get("database") or "default",
        connect_timeout=extra.get("connect_timeout", 10),
        send_receive_timeout=extra.get("send_receive_timeout", 300),
    )


def init_clickhouse(**_):
    log.info("Connecting to ClickHouse via connection=%s", CH_CONN_ID)
    ch = get_clickhouse_client()

    version = ch.command("SELECT version()")
    log.info("Connected to ClickHouse, version=%s", version)

    ch.command("CREATE DATABASE IF NOT EXISTS reports")

    ch.command("""
      CREATE TABLE IF NOT EXISTS reports.crm_clients_dim
      (
        email String,
        first_name String,
        last_name String,
        country String,
        updated_at DateTime
      )
      ENGINE = ReplacingMergeTree(updated_at)
      ORDER BY (email)
    """)

    ch.command("""
      CREATE TABLE IF NOT EXISTS reports.crm_client_prosthesis_dim
      (
        email String,
        prosthesis_id String,
        is_active UInt8,
        updated_at DateTime
      )
      ENGINE = ReplacingMergeTree(updated_at)
      ORDER BY (email, prosthesis_id)
    """)

    log.info("ClickHouse init done")


def extract_transform_load(**_):
    wm = get_watermark()
    new_wm = utc_now_iso()

    log.info("Watermark=%s", wm)

    crm = PostgresHook(postgres_conn_id=CRM_CONN_ID)

    clients = crm.get_records(
        """
        SELECT email, first_name, last_name, country, updated_at
        FROM crm_clients
        WHERE updated_at > %(wm)s
        ORDER BY updated_at
        """,
        parameters={"wm": wm},
    )

    links = crm.get_records(
        """
        SELECT email, prosthesis_id::text, is_active, updated_at
        FROM crm_client_prosthesis
        WHERE updated_at > %(wm)s
        ORDER BY updated_at
        """,
        parameters={"wm": wm},
    )

    log.info("Fetched from CRM: clients=%d links=%d", len(clients), len(links))

    ch = get_clickhouse_client()

    if clients:
        ch.insert(
            "reports.crm_clients_dim",
            clients,
            column_names=["email", "first_name", "last_name", "country", "updated_at"],
        )

    if links:
        links_norm = [(c, p, 1 if a else 0, u) for (c, p, a, u) in links]
        ch.insert(
            "reports.crm_client_prosthesis_dim",
            links_norm,
            column_names=["email", "prosthesis_id", "is_active", "updated_at"],
        )

    set_watermark(new_wm)
    log.info("ETL done, new watermark=%s", new_wm)


default_args = {"owner": "bionicpro", "retries": 2, "retry_delay": timedelta(minutes=5)}

with DAG(
    dag_id=DAG_ID,
    start_date=datetime(2026, 2, 1),
    schedule=SCHEDULE,
    catchup=False,
    default_args=default_args,
    tags=["etl", "crm", "clickhouse"],
) as dag:
    t_init = PythonOperator(task_id="init_clickhouse", python_callable=init_clickhouse)
    t_etl = PythonOperator(task_id="etl_crm_to_clickhouse", python_callable=extract_transform_load)

    t_init >> t_etl

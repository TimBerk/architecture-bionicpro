#!/usr/bin/env bash

airflow connections add crm_pg \
  --conn-uri 'postgresql://crm:crm@crm-db:5432/crm' || true

airflow connections add clickhouse_reports \
  --conn-uri 'http://default:pass:@clickhouse:8123/' || true

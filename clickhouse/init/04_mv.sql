DROP VIEW IF EXISTS reports.mv_crm_clients_queue_to_raw;
CREATE MATERIALIZED VIEW reports.mv_crm_clients_queue_to_raw
TO reports.crm_clients_cdc_raw
AS
SELECT
  now() AS ingesttime,
  payload
FROM reports.crm_clients_cdc_queue;

DROP VIEW IF EXISTS reports.mv_crm_client_prosthesis_queue_to_raw;
CREATE MATERIALIZED VIEW reports.mv_crm_client_prosthesis_queue_to_raw
TO reports.crm_client_prosthesis_cdc_raw
AS
SELECT
  now() AS ingesttime,
  payload
FROM reports.crm_client_prosthesis_cdc_queue;

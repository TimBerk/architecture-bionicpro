DROP TABLE IF EXISTS reports.crm_clients_cdc_raw;
CREATE TABLE reports.crm_clients_cdc_raw
(
  ingesttime DateTime DEFAULT now(),
  payload String
)
ENGINE = MergeTree
ORDER BY ingesttime;

DROP TABLE IF EXISTS reports.crm_client_prosthesis_cdc_raw;
CREATE TABLE reports.crm_client_prosthesis_cdc_raw
(
  ingesttime DateTime DEFAULT now(),
  payload String
)
ENGINE = MergeTree
ORDER BY ingesttime;

DROP VIEW IF EXISTS reports.mv_crm_clients_raw_to_dim;

CREATE MATERIALIZED VIEW reports.mv_crm_clients_raw_to_dim
TO reports.crm_clients_dim
AS
SELECT
  assumeNotNull(JSONExtractString(payload, 'payload', 'after', 'email'))   AS email,
  assumeNotNull(JSONExtractString(payload, 'payload', 'after', 'country')) AS country,
  assumeNotNull(parseDateTime64BestEffortOrNull(
    JSONExtractString(payload, 'payload', 'after', 'updated_at')
  )) AS updated_at
FROM reports.crm_clients_cdc_raw
WHERE
  JSONExtractString(payload, 'payload', 'op') IN ('c','u','r')
  AND JSONExtractString(payload, 'payload', 'after', 'email') IS NOT NULL
  AND parseDateTime64BestEffortOrNull(JSONExtractString(payload, 'payload', 'after', 'updated_at')) IS NOT NULL;


DROP VIEW IF EXISTS reports.mv_crmclient_prosthesis_raw_to_dim;

CREATE MATERIALIZED VIEW reports.mv_crm_client_prosthesis_raw_to_dim
TO reports.crm_client_prosthesis_dim
AS
SELECT
  assumeNotNull(JSONExtractString(payload, 'payload', 'after', 'email'))        AS email,
  assumeNotNull(JSONExtractString(payload, 'payload', 'after', 'prosthesis_id')) AS prosthesis_id,
  assumeNotNull(toUInt8(toNullable(JSONExtractBool(payload, 'payload', 'after', 'is_active')))) AS is_active,
  assumeNotNull(parseDateTime64BestEffortOrNull(
    JSONExtractString(payload, 'payload', 'after', 'updatedat')
  )) AS updated_at
FROM reports.crm_client_prosthesis_cdc_raw
WHERE
  JSONExtractString(payload, 'payload', 'op') IN ('c','u','r')
  AND JSONExtractString(payload, 'payload', 'after', 'email') IS NOT NULL
  AND JSONExtractString(payload, 'payload', 'after', 'prosthesis_id') IS NOT NULL
  AND parseDateTime64BestEffortOrNull(JSONExtractString(payload, 'payload', 'after', 'updated_at')) IS NOT NULL;

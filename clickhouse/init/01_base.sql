CREATE DATABASE IF NOT EXISTS reports;

-- Таблицы ровно под твой отчёт:
DROP TABLE IF EXISTS reports.crm_clients_dim;

CREATE TABLE reports.crm_clients_dim
(
  email String,
  country String,
  updated_at DateTime64(6, 'UTC')
)
ENGINE = ReplacingMergeTree(updated_at)
ORDER BY email;

DROP TABLE IF EXISTS reports.crm_client_prosthesis_dim;

CREATE TABLE reports.crm_client_prosthesis_dim
(
  email String,
  prosthesis_id String,
  is_active UInt8,
  updated_at DateTime64(6, 'UTC')
)
ENGINE = ReplacingMergeTree(updated_at)
ORDER BY (email, prosthesis_id);

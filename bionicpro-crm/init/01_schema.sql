BEGIN;

DROP TABLE IF EXISTS crm_client_prosthesis;
DROP TABLE IF EXISTS crm_prostheses;
DROP TABLE IF EXISTS crm_clients;

CREATE TABLE crm_clients (
  email       TEXT PRIMARY KEY,          -- unique id
  first_name  TEXT NOT NULL,
  last_name   TEXT NOT NULL,
  country     TEXT NOT NULL,
  updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE crm_prostheses (
  prosthesis_id TEXT PRIMARY KEY,
  model         TEXT NOT NULL,
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE crm_client_prosthesis (
  email         TEXT NOT NULL REFERENCES crm_clients(email) ON DELETE CASCADE,
  prosthesis_id TEXT NOT NULL REFERENCES crm_prostheses(prosthesis_id) ON DELETE CASCADE,
  is_active     BOOLEAN NOT NULL DEFAULT true,
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (email, prosthesis_id)
);

CREATE INDEX IF NOT EXISTS crm_clients_updated_at_idx
  ON crm_clients(updated_at);

CREATE INDEX IF NOT EXISTS crm_client_prosthesis_updated_at_idx
  ON crm_client_prosthesis(updated_at);

COMMIT;

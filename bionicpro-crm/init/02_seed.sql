BEGIN;

-- 1) clients: 3 base + 10 more
WITH input_clients AS (
  SELECT * FROM (VALUES
    ('user1@example.com',      'User',      'One', 'RU'),
    ('user2@example.com',      'User',      'Two', 'RU'),
    ('prothetic1@example.com', 'Prothetic', 'One', 'RU')
  ) v(email, first_name, last_name, country)

  UNION ALL

  SELECT
    format('user%02s@example.com', g) AS email,       -- user04..user13 (10 rows)
    initcap(format('user%02s', g))    AS first_name,
    'Test'                            AS last_name,
    'RU'                              AS country
  FROM generate_series(4, 13) AS g
)
INSERT INTO crm_clients (email, first_name, last_name, country)
SELECT email, first_name, last_name, country
FROM input_clients
ON CONFLICT (email) DO UPDATE
SET first_name = EXCLUDED.first_name,
    last_name  = EXCLUDED.last_name,
    country    = EXCLUDED.country,
    updated_at = now();

-- 2) prostheses: 3 base + 10 more
WITH input_prostheses AS (
  SELECT * FROM (VALUES
    ('pr-001', 'BionicArm X'),
    ('pr-002', 'BionicArm X'),
    ('pr-003', 'BionicLeg Z')
  ) v(prosthesis_id, model)

  UNION ALL

  SELECT
    format('pr-%03s', g) AS prosthesis_id,            -- pr-010..pr-019
    CASE WHEN g % 2 = 0 THEN 'BionicArm X' ELSE 'BionicLeg Z' END AS model
  FROM generate_series(10, 19) AS g
)
INSERT INTO crm_prostheses (prosthesis_id, model)
SELECT prosthesis_id, model
FROM input_prostheses
ON CONFLICT (prosthesis_id) DO UPDATE
SET model = EXCLUDED.model,
    updated_at = now();

-- 3) links: 3 base + 10 more (email↔prosthesis_id)
WITH input_links AS (
  SELECT * FROM (VALUES
    ('user1@example.com',      'pr-001', true),
    ('user2@example.com',      'pr-002', true),
    ('prothetic1@example.com', 'pr-003', true)
  ) v(email, prosthesis_id, is_active)

  UNION ALL

  SELECT
    format('user%02s@example.com', g) AS email,
    format('pr-%03s', 6 + g)          AS prosthesis_id, -- 4->10 ... 13->19
    (g % 2 = 0)                       AS is_active
  FROM generate_series(4, 13) AS g
)
INSERT INTO crm_client_prosthesis (email, prosthesis_id, is_active)
SELECT email, prosthesis_id, is_active
FROM input_links
ON CONFLICT (email, prosthesis_id) DO UPDATE
SET is_active = EXCLUDED.is_active,
    updated_at = now();

COMMIT;

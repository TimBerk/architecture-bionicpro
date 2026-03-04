-- 1) Роль/пользователь для Debezium
CREATE ROLE dbz_replication WITH REPLICATION LOGIN;
CREATE USER debezium WITH PASSWORD 'dbz_pass';
GRANT dbz_replication TO debezium;

-- 2) Права на чтение данных для snapshot и (если нужно) чтение таблиц
GRANT CONNECT ON DATABASE crm TO debezium;
\c crm

GRANT USAGE ON SCHEMA public TO debezium;
GRANT SELECT ON TABLE public.crm_clients TO debezium;
GRANT SELECT ON TABLE public.crm_client_prosthesis TO debezium;
GRANT SELECT ON TABLE public.crm_prostheses TO debezium;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO debezium;
ALTER ROLE debezium WITH REPLICATION;

-- 3) Создание публикации для всех таблиц
CREATE PUBLICATION dbz_publication FOR ALL TABLES;

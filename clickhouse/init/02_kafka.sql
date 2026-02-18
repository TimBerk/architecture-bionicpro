DROP TABLE IF EXISTS reports.crm_clients_cdc_queue;
CREATE TABLE reports.crm_clients_cdc_queue
(
  payload String
)
ENGINE = Kafka
SETTINGS
  kafka_broker_list = 'redpanda:9092',
  kafka_topic_list = 'crm.public.crm_clients',
  kafka_group_name = 'ch_reports_cdc',
  kafka_format = 'JSONAsString',
  kafka_num_consumers = 1;

DROP TABLE IF EXISTS reports.crm_client_prosthesis_cdc_queue;
CREATE TABLE reports.crm_client_prosthesis_cdc_queue
(
  payload String
)
ENGINE = Kafka
SETTINGS
  kafka_broker_list = 'redpanda:9092',
  kafka_topic_list = 'crm.public.crm_client_prosthesis',
  kafka_group_name = 'ch_reports_cdc',
  kafka_format = 'JSONAsString',
  kafka_num_consumers = 1;

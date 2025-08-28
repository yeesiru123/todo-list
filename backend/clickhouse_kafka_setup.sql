-- ClickHouse Kafka Engine Table
CREATE TABLE IF NOT EXISTS todo_events_kafka (
    event_id String,
    event_type String,
    todo_id String,
    title String,
    description String,
    is_done UInt8,
    user_id String,
    timestamp DateTime
) ENGINE = Kafka
SETTINGS
    kafka_broker_list = 'kafka:9092',
    kafka_topic_list = 'todo_events',
    kafka_group_name = 'clickhouse_todo_group',
    kafka_format = 'JSONEachRow',
    kafka_num_consumers = 1;

-- Destination Table
CREATE TABLE IF NOT EXISTS todo_events (
    event_id String,
    event_type String,
    todo_id String,
    title String,
    description String,
    is_done UInt8,
    user_id String,
    timestamp DateTime
) ENGINE = MergeTree()
ORDER BY (timestamp, event_id);

-- Materialized View
CREATE MATERIALIZED VIEW IF NOT EXISTS todo_events_mv TO todo_events AS
SELECT
    event_id,
    event_type,
    todo_id,
    title,
    description,
    is_done,
    user_id,
    timestamp
FROM todo_events_kafka;

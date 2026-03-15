import os
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import EnvironmentSettings, StreamTableEnvironment

def run_q4():
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_parallelism(1) # CRUCIAL para el homework
    
    settings = EnvironmentSettings.new_instance().in_streaming_mode().build()
    t_env = StreamTableEnvironment.create(env, environment_settings=settings)

    # 1. Source: Redpanda
    t_env.execute_sql("""
        CREATE TABLE green_trips (
            lpep_pickup_datetime STRING,
            PULocationID INT,
            -- Definimos el tiempo del evento y el watermark
            event_timestamp AS TO_TIMESTAMP(lpep_pickup_datetime, 'yyyy-MM-dd HH:mm:ss'),
            WATERMARK FOR event_timestamp AS event_timestamp - INTERVAL '5' SECOND
        ) WITH (
            'connector' = 'kafka',
            'topic' = 'green-trips',
            'properties.bootstrap.servers' = '07-streaming-axl-redpanda-1:29092',
            'properties.group.id' = 'q4-group',
            'scan.startup.mode' = 'earliest-offset',
            'format' = 'json'
        );
    """)

    # 2. Sink: Postgres
    t_env.execute_sql("""
        CREATE TABLE q4_sink (
            window_start TIMESTAMP(3),
            PULocationID INT,
            num_trips BIGINT
        ) WITH (
            'connector' = 'jdbc',
            'url' = 'jdbc:postgresql://07-streaming-axl-postgres-1:5432/postgres',
            'table-name' = 'q4_pickup_stats',
            'username' = 'postgres',
            'password' = 'postgres'
        );
    """)

    # 3. Query: Tumbling Window 5 min
    t_env.execute_sql("""
        INSERT INTO q4_sink
        SELECT 
            window_start, 
            PULocationID, 
            COUNT(*) as num_trips
        FROM TABLE(
            TUMBLE(TABLE green_trips, DESCRIPTOR(event_timestamp), INTERVAL '5' MINUTES)
        )
        GROUP BY window_start, window_end, PULocationID;
    """).wait()

if __name__ == '__main__':
    run_q4()
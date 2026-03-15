from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import EnvironmentSettings, StreamTableEnvironment

def run_q6():
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_parallelism(1)
    
    settings = EnvironmentSettings.new_instance().in_streaming_mode().build()
    t_env = StreamTableEnvironment.create(env, environment_settings=settings)

    # SOURCE
    t_env.execute_sql("""
        CREATE TABLE green_trips (
            lpep_pickup_datetime STRING,
            tip_amount DOUBLE,
            event_timestamp AS TO_TIMESTAMP(lpep_pickup_datetime, 'yyyy-MM-dd HH:mm:ss'),
            WATERMARK FOR event_timestamp AS event_timestamp - INTERVAL '5' SECOND
        ) WITH (
            'connector' = 'kafka',
            'topic' = 'green-trips',
            'properties.bootstrap.servers' = 'redpanda:29092',
            'properties.group.id' = 'q6-final-group',
            'scan.startup.mode' = 'earliest-offset',
            'format' = 'json',
            'json.ignore-parse-errors' = 'true'
        );
    """)

    # SINK
    t_env.execute_sql("""
        CREATE TABLE q6_sink (
            window_start TIMESTAMP(3),
            total_tip_amount DOUBLE PRECISION,
            PRIMARY KEY (window_start) NOT ENFORCED
        ) WITH (
            'connector' = 'jdbc',
            'url' = 'jdbc:postgresql://postgres:5432/postgres',
            'table-name' = 'q6_tip_stats',
            'username' = 'postgres',
            'password' = 'postgres'
        );
    """)

    t_env.execute_sql("""
        INSERT INTO q6_sink
        SELECT window_start, SUM(tip_amount) as total_tip_amount
        FROM TABLE(
            TUMBLE(TABLE green_trips, DESCRIPTOR(event_timestamp), INTERVAL '1' HOURS)
        )
        GROUP BY window_start, window_end;
    """).wait()

if __name__ == '__main__':
    run_q6()
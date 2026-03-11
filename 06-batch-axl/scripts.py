python 06_spark_sql2.py \
    --input_green=data/pq/green/2020/*/ \
    --input_yellow=data/pq/yellow/2020/*/ \
    --output=data/report/revenue/

URL="spark://DESKTOP-AEBMQ4R.localdomain:7077"


spark-submit \
    --master spark://127.0.0.1:7077 \
    06_spark_sql2.py \
        --input_green=data/pq/green/2020/*/ \
        --input_yellow=data/pq/yellow/2020/*/ \
        --output=data/report/revenue/




--input_green=gs://dtc_data_lake_de-zoomcamp-nytaxi-axl/pq/green/2020/*/ \
--input_yellow=gs://dtc_data_lake_de-zoomcamp-nytaxi-axl/pq/yellow/2020/*/ \
--output=gs://dtc_data_lake_de-zoomcamp-nytaxi-axl/report/revenue/



gcloud dataproc jobs submit pyspark \
    --cluster=cluster-fdfa \
    --region=us-central1 \
    gs://dtc_data_lake_de-zoomcamp-nytaxi-axl/code/06_spark_sql2_bigquery.py \
    -- \
        --input_green=gs://dtc_data_lake_de-zoomcamp-nytaxi-axl/pq/green/2020/*/ \
        --input_yellow=gs://dtc_data_lake_de-zoomcamp-nytaxi-axl/pq/yellow/2020/*/ \
        --output=trips_data_all.reports-2020
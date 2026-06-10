from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='hockey_pipeline',
    default_args=default_args,
    description='Ingest NHL data and run dbt transformations',
    schedule='0 6 * * *',  # runs every day at 6am
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['hockey'],
) as dag:

    ingest_nhl_data = BashOperator(
        task_id='ingest_nhl_data',
        bash_command='python /opt/airflow/dags/nhl_ingest.py',
    )

    dbt_run = BashOperator(
        task_id='dbt_run',
        bash_command='cd /opt/airflow/dags/hockey_dbt && dbt run --profiles-dir /opt/airflow/.dbt',
    )

    dbt_test = BashOperator(
        task_id='dbt_test',
        bash_command='cd /opt/airflow/dags/hockey_dbt && dbt test --profiles-dir /opt/airflow/.dbt',
    )

    # Define task dependencies
    ingest_nhl_data >> dbt_run >> dbt_test
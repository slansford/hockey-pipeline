import sys
import os

scripts_path = '/opt/airflow/scripts' if os.path.exists('/opt/airflow/scripts') else os.path.join(os.path.dirname(__file__), '../../scripts')
sys.path.insert(0, scripts_path)  #Adds script path to Python import directories

from datetime import datetime
from airflow.decorators import dag, task # type: ignore

@dag(
    schedule='0 9 * * *',
    start_date=datetime(2026, 6, 1),
    catchup=False,
    tags=['hockey']
)
def hockey_pipeline():
    """
    Simple data pipeline using Airflow TaskFlow API to load data from the NHL API into BigQuery, builds dbt staging and mart layers, tests them, and then updates an Elasticsearch index with that data.
    
    """
    @task()
    def ingest_nhl_data() -> None:
        """
        Loads data from the NHL API into BigQuery.
        """
        import nhl_ingest
        nhl_ingest.run()

    @task.bash()
    def dbt_run() -> str:
        """
        Builds staging and mart layers with dbt in BigQuery.
        """
        return 'dbt run --project-dir /opt/airflow/dbt --profiles-dir /opt/airflow/.dbt'
    
    @task.bash()
    def dbt_test() -> str:
        """
        Tests staging and mart layers with dbt.
        """
        return 'dbt test --project-dir /opt/airflow/dbt --profiles-dir /opt/airflow/.dbt'


    ingest_nhl_data() >> dbt_run() >> dbt_test()

hockey_pipeline()
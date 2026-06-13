import os
import requests
from google.cloud import bigquery

def run() -> None:
    """
    Entry point for DAG

    Args:
        None

    Returns:
        None
    
    """

    endpoints = ["skater", "goalie", "team"]

    for endpoint in endpoints:
        data = get_stats(endpoint=endpoint)
        load_to_bigquery(data, endpoint)

def get_stats(endpoint: str) -> list[dict]:
    """
    Fetches skater, goalie, and team stats from the NHL api for a given season.

    Args:
        endpoint: Must be 'skater', 'goalie', or 'team'

    Returns:
        List of endpoint stat dictionaries
    
    """

    season = "20232024"

    url = f"https://api.nhle.com/stats/rest/en/{endpoint}/summary"
    params = {
        "isAggregate": "false",
        "isGame": "false",
        "start": 0,
        "limit": -1,
        "cayenneExp": f"gameTypeId=2 and seasonId<={season} and seasonId>={season}"
    }

    response = requests.get(url=url, params=params)
    response.raise_for_status()
    return response.json()["data"]

def load_to_bigquery(data: list[dict], table: str) -> None:
    """
    Loads data from NHL endpoint into the appropriate BigQuery table.

    Args:
        data: List of dictionary data returned from NHL API

        table: Name of table to load data into; same name as endpoint

    Returns:
        None
    
    """

    project_id = os.environ.get('GOOGLE_CLOUD_PROJECT')
    dataset = "hockey_raw"

    client = bigquery.Client(project=project_id)

    #Checks for dataset and creates it if it doesn't exist
    dataset_ref = bigquery.Dataset(f"{project_id}.{dataset}")
    dataset_ref.location = "US"
    client.create_dataset(dataset_ref, exists_ok=True)

    #Creates table reference and configures load job
    table_ref = f"{project_id}.{dataset}.{table}"
    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE, #if table exists, delete all rows and add new ones
        autodetect=True
    )

    #Loads data into table within dataset
    job = client.load_table_from_json(
        data,
        table_ref,
        job_config=job_config
    )

    #Waits for job to complete
    job.result()
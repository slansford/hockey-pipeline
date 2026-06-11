import requests, os
from google.cloud import bigquery

# Config
PROJECT_ID = os.environ.get('GCP_PROJECT_ID', 'your-project-id')
DATASET = "hockey_raw"
TABLE = "skaters"
SEASON = "20232024"

def get_skater_stats(season: str) -> list[dict]:
    url = f"https://api.nhle.com/stats/rest/en/skater/summary"
    params = {
        "isAggregate": "false",
        "isGame": "false",
        "start": 0,
        "limit": -1,
        "cayenneExp": f"gameTypeId=2 and seasonId<={SEASON} and seasonId>={SEASON}" # wtf is this
    }

    response = requests.get(url=url, params=params)
    response.raise_for_status()
    return response.json()["data"]

def get_goalie_stats(season: str) -> list[dict]:
    url = "https://api.nhle.com/stats/rest/en/goalie/summary"
    params = {
        "isAggregate": "false",
        "isGame": "false",
        "start": 0,
        "limit": -1,
        "cayenneExp": f"gameTypeId=2 and seasonId<={season} and seasonId>={season}"
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()["data"]

def get_team_stats(season: str) -> list[dict]:
    url = "https://api.nhle.com/stats/rest/en/team/summary"
    params = {
        "isAggregate": "false",
        "isGame": "false",
        "start": 0,
        "limit": -1,
        "cayenneExp": f"gameTypeId=2 and seasonId<={season} and seasonId>={season}"
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()["data"]

def load_to_bq(rows: list[dict], project: str, dataset: str, table: str):

    client = bigquery.Client(project=project)

    # Creates the dataset if it doesn't exist
    dataset_ref = bigquery.Dataset(f"{project}.{dataset}")
    dataset_ref.location = "US"
    client.create_dataset(dataset_ref, exists_ok=True)

    # Load data into dataset
    table_ref = f"{project}.{dataset}.{table}"
    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE, # wtf is write disposition?
        autodetect=True # schema inference
    )

    job = client.load_table_from_json(
        rows,
        table_ref,
        job_config=job_config
    )

    job.result() # wait for job to complete
    print(f"Loaded {len(rows)} rows into {table_ref}")

if __name__ == "__main__":
    for entity, fn, table in [
        ("skater", get_skater_stats, "skaters"),
        ("goalie", get_goalie_stats, "goalies"),
        ("team", get_team_stats, "teams"),
    ]:
        print(f"Fetching {entity} stats for season {SEASON}...")
        rows = fn(SEASON)
        print(f"Got {len(rows)} records")
        load_to_bq(rows, PROJECT_ID, DATASET, table)
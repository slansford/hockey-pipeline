import os
from google.cloud import bigquery
from elasticsearch import Elasticsearch

def run() -> None:
    """
    Entry point for DAG

    Args:
        None

    Returns:
        None
    
    """

    data = get_skater_stats_from_bigquery()

    index_to_elasticsearch(data)

def get_skater_stats_from_bigquery() -> list[dict]:
    """
    Retrieves skater stats from dbt mart housed in BigQuery

    Args:
        None

    Returns:
        List of skater stats in dictionary format
    """

    project_id = os.environ.get('GOOGLE_CLOUD_PROJECT')
    client = bigquery.Client(project=project_id)
    query = f"select * from `{project_id}.hockey_dbt_dev.mart_skater_stats`"

    results = client.query(query).result()

    return [dict(row) for row in results]

def index_to_elasticsearch(data: list[dict]) -> None:
    """
    Indexes skater data retreived from BigQuery into Elasticsearch

    Args:
        List of skater stats in dictionary format

    Returns:
        None
    """

    host = os.environ.get('ES_HOST')
    es = Elasticsearch(host)
    index = 'skater_stats'
    
    #Clears out any existing matching indices
    if es.indices.exists(index=index):
        es.indices.delete(index=index)
    
    #Creates index
    es.indices.create(index=index, body={
        "mappings": {
            "properties": {
                "player_id":        {"type": "integer"},
                "player_name":      {"type": "text"},
                "team":             {"type": "keyword"},
                "position":         {"type": "keyword"},
                "games_played":     {"type": "integer"},
                "goals":            {"type": "integer"},
                "assists":          {"type": "integer"},
                "points":           {"type": "integer"},
                "points_per_game":  {"type": "float"},
                "goals_per_game":   {"type": "float"},
                "shooting_pct":     {"type": "float"},
                "toi_per_game":     {"type": "float"}
            }
        }
    })
    
    #Bulk indexes skater stats as documents
    for record in data:
        es.index(
            index=index,
            id=record['player_id'],
            document=record
        )

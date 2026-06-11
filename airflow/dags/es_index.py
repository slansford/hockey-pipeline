import os
from google.cloud import bigquery
from elasticsearch import Elasticsearch

PROJECT_ID = os.environ.get('GCP_PROJECT_ID')
ES_HOST = os.environ.get('ES_HOST', 'http://elasticsearch:9200')
INDEX_NAME = 'skater_stats'

def get_skater_stats_from_bq() -> list[dict]:
    client = bigquery.Client(project=PROJECT_ID)
    query = """
        select *
        from `{}.hockey_dbt_dev.mart_skater_stats`
    """.format(PROJECT_ID)
    
    results = client.query(query).result()
    return [dict(row) for row in results]

def index_to_elasticsearch(rows: list[dict]):
    es = Elasticsearch(ES_HOST)
    
    #clears out any existing indices
    if es.indices.exists(index=INDEX_NAME):
        es.indices.delete(index=INDEX_NAME)
    
    #creates indices
    es.indices.create(index=INDEX_NAME, body={
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
    
    #mass-indexes documents
    for row in rows:
        es.index(
            index=INDEX_NAME,
            id=row['player_id'],
            document=row
        )
    
    print(f"Indexed {len(rows)} skaters into Elasticsearch")

if __name__ == "__main__":
    print("Fetching skater stats from BigQuery...")
    rows = get_skater_stats_from_bq()
    print(f"Got {len(rows)} rows")
    index_to_elasticsearch(rows)
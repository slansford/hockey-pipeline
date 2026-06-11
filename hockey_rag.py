import json
import os
import anthropic
from elasticsearch import Elasticsearch

ES_HOST = "http://localhost:9200"
INDEX_NAME = "skater_stats"

def generate_es_query(question: str) -> dict:
    """Use Claude to convert a natural language question into an ES query"""
    client = anthropic.Anthropic()
    
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": f"""You are an Elasticsearch query generator for NHL hockey stats.

The index contains these fields:
- player_name (text) — full name e.g. "Connor McDavid"
- team (keyword) — 3 letter abbreviation e.g. "EDM", "TOR", "BOS"
- position (keyword) — "C", "L", "R", "D"
- games_played (integer)
- goals (integer)
- assists (integer)
- points (integer)
- plus_minus (integer)
- penalty_minutes (integer)
- power_play_goals (integer)
- power_play_points (integer)
- short_handed_goals (integer)
- shots (integer)
- shooting_pct (float) — e.g. 0.152 means 15.2%
- toi_per_game (float) — time on ice in seconds per game
- goals_per_game (float)
- assists_per_game (float)
- points_per_game (float)
- shots_per_game (float)

Convert this question into a valid Elasticsearch query JSON object.
Return ONLY the raw JSON query object, no explanation, no markdown, no backticks.

Question: {question}"""
            }
        ]
    )
    
    raw = message.content[0].text.strip()
    return json.loads(raw)


def search_elasticsearch(question: str, size: int = 10) -> list[dict]:
    es = Elasticsearch(ES_HOST)
    
    print("Generating Elasticsearch query...")
    es_query = generate_es_query(question)
    print(f"Query: {json.dumps(es_query, indent=2)}")
    
    response = es.search(index=INDEX_NAME, body={**es_query, "size": size})
    return [hit["_source"] for hit in response["hits"]["hits"]]


def ask_claude(question: str, context: list[dict]) -> str:
    client = anthropic.Anthropic()
    
    context_str = "\n".join([
        f"{p.get('player_name')} ({p.get('position')}, {p.get('team')}): "
        f"{p.get('games_played')} GP, {p.get('goals')} G, {p.get('assists')} A, "
        f"{p.get('points')} PTS, {p.get('points_per_game')} P/GP, "
        f"{p.get('shooting_pct', 0):.3f} SH%, "
        f"{p.get('plus_minus')} +/-, "
        f"{p.get('power_play_goals')} PPG, {p.get('power_play_points')} PPP"
        for p in context
    ])
    
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": f"""You are a hockey analytics assistant.
Use the following player data to answer the question.

Player Data:
{context_str}

Question: {question}

Answer based only on the data provided."""
            }
        ]
    )
    
    return message.content[0].text


def hockey_rag(question: str):
    print(f"\nQuestion: {question}")
    print("Searching player data...")
    
    context = search_elasticsearch(question)
    
    if not context:
        print("No relevant players found")
        return
    
    print(f"Found {len(context)} relevant players, asking Claude...")
    answer = ask_claude(question, context)
    print(f"\nAnswer: {answer}")


if __name__ == "__main__":
    hockey_rag("Tell me about Connor McDavid's season")
    hockey_rag("Who are the best snipers on the Oilers?")
    hockey_rag("Which defensemen have the best plus minus?")
    hockey_rag("Who are the top power play performers?")
import os

def write_env(path: str, values: dict):
    """
    Writes environment variables to a .env file.
    
    Args:
        path: Path to the .env file
        values: Dictionary of environment variables to write
    
    Returns:
        None
    """
    lines = []
    if os.path.exists(path):
        with open(path) as f:
            lines = f.readlines()
    
    existing_keys = {l.split('=')[0] for l in lines if '=' in l}
    
    with open(path, 'a') as f:
        for key, value in values.items():
            if key not in existing_keys:
                f.write(f"{key}={value}\n")
    
    print(f"Updated {path}")

def setup_alias():
    """
    Adds the 'hockey' alias to ~/.bashrc.
    
    Args:
        None
    
    Returns:
        None
    """
    bashrc_path = os.path.expanduser("~/.bashrc")
    alias_line = f"alias hockey='python {os.path.expanduser('~/hockey-pipeline/rag/hockey_rag.py')}'"
    
    with open(bashrc_path) as f:
        if alias_line in f.read():
            print("Alias already set")
            return
    
    with open(bashrc_path, 'a') as f:
        f.write(f"\n{alias_line}\n")
    
    print("Added 'hockey' alias to ~/.bashrc")
    print("Run 'source ~/.bashrc' or restart your terminal to use it")

def setup():
    """
    Entry point for project setup.
    
    Args:
        None
    
    Returns:
        None
    """
    print("\n--- Hockey Pipeline Setup ---\n")
    
    project_id = input("GCP Project ID: ").strip()
    dataset = input("BigQuery dataset name (default: hockey_raw): ").strip() or "hockey_raw"
    anthropic_key = input("Anthropic API key: ").strip()
    
    #write to airflow .env
    write_env("airflow/.env", {
        "GOOGLE_CLOUD_PROJECT": project_id,
        "ANTHROPIC_API_KEY": anthropic_key,
        "AIRFLOW_UID": str(os.getuid()),
    })
    
    #write dbt profiles.yml
    profiles = f"""hockey_dbt:
  target: dev
  outputs:
    dev:
      type: bigquery
      method: oauth
      project: {project_id}
      dataset: hockey_dbt_dev
      threads: 4
      location: US
    prod:
      type: bigquery
      method: oauth
      project: {project_id}
      dataset: hockey_dbt
      threads: 4
      location: US
"""
    profiles_dir = os.path.expanduser("~/.dbt")
    os.makedirs(profiles_dir, exist_ok=True)
    with open(f"{profiles_dir}/profiles.yml", "w") as f:
        f.write(profiles)
    print("Updated ~/.dbt/profiles.yml")
    
    # Set up alias
    setup_alias()
    
    print("\n=== Setup complete ===")
    print("Next steps:")
    print("  1. Run: gcloud auth application-default login")
    print("  2. Run: source ~/.bashrc")
    print("  3. Run: cd airflow && docker compose up -d")
    print("  4. Open: http://localhost:8080")
    print("  5. Query: hockey 'who has the most points?'")

if __name__ == "__main__":
    setup()
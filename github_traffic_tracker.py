import os
import logging
from dotenv import load_dotenv
import requests
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError
import yaml

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

# Load repositories from repos.yaml
def load_repositories():
    with open('repos.yaml', 'r') as f:
        data = yaml.safe_load(f)
        return [(item['owner'], item['repo']) for item in data['repos']]

REPOSITORIES = load_repositories()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
SUPABASE_HOST = os.getenv("SUPABASE_HOST")
SUPABASE_DB = os.getenv("SUPABASE_DB")
SUPABASE_USER = os.getenv("SUPABASE_USER")
SUPABASE_PASSWORD = os.getenv("SUPABASE_PASSWORD")
SUPABASE_PORT = os.getenv("SUPABASE_PORT", "5432")

DB_URL = f"postgresql://{SUPABASE_USER}:{SUPABASE_PASSWORD}@{SUPABASE_HOST}:{SUPABASE_PORT}/{SUPABASE_DB}"

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# Database connection setup
def get_db_connection():
    try:
        engine = create_engine(DB_URL)
        conn = engine.connect()
        return conn
    except Exception as e:
        logging.error(f"Database connection failed: {e}")
        raise

# GitHub API fetch functions
def fetch_github_traffic(owner, repo, token):
    base_url = f"https://api.github.com/repos/{owner}/{repo}/traffic"
    try:
        views_resp = requests.get(f"{base_url}/views", headers=HEADERS)
        clones_resp = requests.get(f"{base_url}/clones", headers=HEADERS)
        views_resp.raise_for_status()
        clones_resp.raise_for_status()
        views = views_resp.json().get("views", [])
        clones = clones_resp.json().get("clones", [])
        return views, clones
    except Exception as e:
        logging.error(f"Failed to fetch traffic for {owner}/{repo}: {e}")
        return [], []

def upsert_traffic_metric(conn, repo_name, day, unique_views, total_views, unique_clones, total_clones):
    sql = text('''
        INSERT INTO github_traffic (repo_name, timestamp, unique_views, total_views, unique_clones, total_clones)
        VALUES (:repo_name, :timestamp, :unique_views, :total_views, :unique_clones, :total_clones)
        ON CONFLICT (repo_name, timestamp) DO UPDATE SET
            unique_views = EXCLUDED.unique_views,
            total_views = EXCLUDED.total_views,
            unique_clones = EXCLUDED.unique_clones,
            total_clones = EXCLUDED.total_clones;
    ''')
    try:
        conn.execute(sql, {
            'repo_name': repo_name,
            'timestamp': day,
            'unique_views': unique_views,
            'total_views': total_views,
            'unique_clones': unique_clones,
            'total_clones': total_clones
        })
        conn.commit()
        logging.info(f"Upserted metrics for {repo_name} on {day}")
    except IntegrityError:
        logging.warning(f"Duplicate entry for {repo_name} on {day}")
    except Exception as e:
        logging.error(f"DB insert failed for {repo_name} on {day}: {e}")

def main():
    if not GITHUB_TOKEN:
        logging.error("GITHUB_TOKEN not set in environment.")
        return
    if not REPOSITORIES:
        logging.error("No repositories configured in REPOSITORIES list.")
        return
    conn = get_db_connection()
    for owner, repo in REPOSITORIES:
        views, clones = fetch_github_traffic(owner, repo, GITHUB_TOKEN)
        # Index by date for easy upsert
        metrics = {}
        for v in views:
            day = v['timestamp'][:10]
            metrics[day] = {
                'unique_views': v['uniques'],
                'total_views': v['count'],
                'unique_clones': 0,
                'total_clones': 0
            }
        for c in clones:
            day = c['timestamp'][:10]
            if day not in metrics:
                metrics[day] = {
                    'unique_views': 0,
                    'total_views': 0,
                    'unique_clones': c['uniques'],
                    'total_clones': c['count']
                }
            else:
                metrics[day]['unique_clones'] = c['uniques']
                metrics[day]['total_clones'] = c['count']
        for day, vals in metrics.items():
            upsert_traffic_metric(
                conn,
                f"{owner}/{repo}",
                day,
                vals['unique_views'],
                vals['total_views'],
                vals['unique_clones'],
                vals['total_clones']
            )
    conn.close()

if __name__ == "__main__":
    main() 
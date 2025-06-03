import os
import argparse
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

parser = argparse.ArgumentParser(description='Visualize GitHub traffic metrics.')
parser.add_argument('--repo', type=str, help='Filter by repository name (owner/repo)')
args = parser.parse_args()

engine = create_engine(
    f"postgresql://{os.getenv('SUPABASE_USER')}:{os.getenv('SUPABASE_PASSWORD')}@{os.getenv('SUPABASE_HOST')}:{os.getenv('SUPABASE_PORT')}/{os.getenv('SUPABASE_DB')}"
)
df = pd.read_sql('SELECT * FROM github_traffic', engine)
df['timestamp'] = pd.to_datetime(df['timestamp'])

print("Available repo_name values:", df['repo_name'].unique())
if args.repo:
    print("You passed --repo:", args.repo)
    df = df[df['repo_name'].str.strip().str.lower() == args.repo.strip().lower()]

print(df)
print("DataFrame shape:", df.shape)
if not df.empty:
    print("Min/Max timestamp:", df['timestamp'].min(), df['timestamp'].max())
    print("total_views:", df['total_views'].values)
    print("total_clones:", df['total_clones'].values)
else:
    print("DataFrame is empty after filtering.")

plt.figure(figsize=(10,5))
for repo in df['repo_name'].unique():
    repo_df = df[df['repo_name'] == repo]
    plt.scatter(repo_df['timestamp'], repo_df['total_views'], label=f'{repo} views')
    plt.scatter(repo_df['timestamp'], repo_df['total_clones'], label=f'{repo} clones')
plt.legend()
plt.title('GitHub Repo Views and Clones Over Time')
plt.xlabel('Date')
plt.ylabel('Count')
plt.show()
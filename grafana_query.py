import yaml

# Load YAML file
with open('repos.yaml', 'r') as f:
    data = yaml.safe_load(f)

repos = data.get("repos", [])

# Start building the query
query_lines = [
    'SELECT',
    '  timestamp AS "time",'
]

for i, repo_entry in enumerate(repos):
    owner = repo_entry["owner"]
    repo = repo_entry["repo"]
    full_name = f"{owner}/{repo}"
    prefix = repo.replace("-", "_").lower()  # For column prefix safety

    query_lines.append(f'  CASE WHEN repo_name = \'{full_name}\' THEN total_views END AS {prefix}_views,')
    query_lines.append(f'  CASE WHEN repo_name = \'{full_name}\' THEN total_clones END AS {prefix}_clones,')

# Add common field
query_lines.append('  repo_name')
query_lines.append('FROM github_traffic')
query_lines.append('WHERE $__timeFilter(timestamp)')
query_lines.append('  AND repo_name IN (')

# Add all repo names in IN clause
repo_names = [f"'{r['owner']}/{r['repo']}'" for r in repos]
query_lines.append('    ' + ', '.join(repo_names))
query_lines.append('  )')
query_lines.append('ORDER BY timestamp;')

# Final query string
sql_query = '\n'.join(query_lines)
print(sql_query)

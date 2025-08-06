import yaml

# Load the YAML file
with open('repos.yaml', 'r') as f:
    data = yaml.safe_load(f)

repos = data.get("repos", [])

# Start building the query for all-time totals
query_lines = [
    'SELECT',
    '  \'All-Time Totals\' AS metric_name,',
    '  SUM(total_views) AS "Total Views",',
    '  SUM(total_clones) AS "Total Clones",',
    '  COUNT(DISTINCT repo_name) AS "Repos Tracked"',
    'FROM github_traffic',
    'WHERE repo_name IN ('
]

# Add all repo names in IN clause
repo_names = [f"'{r['owner']}/{r['repo']}'" for r in repos]
query_lines.append('    ' + ', '.join(repo_names))
query_lines.append('  );')

# Final query string
sql_query = '\n'.join(query_lines)
print("=== Grafana Query for All-Time Totals ===")
print(sql_query) 
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
print("\n=== Alternative Queries ===")

# Alternative 1: Per repository breakdown
print("\n--- Per Repository Breakdown ---")
repo_query_lines = [
    'SELECT',
    '  repo_name,',
    '  SUM(total_views) AS "Total Views",',
    '  SUM(total_clones) AS "Total Clones",',
    '  COUNT(*) AS "Days Tracked"',
    'FROM github_traffic',
    'WHERE repo_name IN ('
]
repo_query_lines.append('    ' + ', '.join(repo_names))
repo_query_lines.append('  )')
repo_query_lines.append('GROUP BY repo_name')
repo_query_lines.append('ORDER BY SUM(total_views) DESC;')

repo_sql_query = '\n'.join(repo_query_lines)
print(repo_sql_query)

# Alternative 2: Time series for daily totals
print("\n--- Time Series (Daily Totals) ---")
time_query_lines = [
    'SELECT',
    '  timestamp AS "time",',
    '  SUM(total_views) AS "Daily Total Views",',
    '  SUM(total_clones) AS "Daily Total Clones"',
    'FROM github_traffic',
    'WHERE $__timeFilter(timestamp)',
    '  AND repo_name IN ('
]
time_query_lines.append('    ' + ', '.join(repo_names))
time_query_lines.append('  )')
time_query_lines.append('GROUP BY timestamp')
time_query_lines.append('ORDER BY timestamp;')

time_sql_query = '\n'.join(time_query_lines)
print(time_sql_query)

# Alternative 3: Cumulative time series
print("\n--- Cumulative Time Series ---")
cumulative_query_lines = [
    'SELECT',
    '  timestamp AS "time",',
    '  SUM(SUM(total_views)) OVER (ORDER BY timestamp) AS "Cumulative Views",',
    '  SUM(SUM(total_clones)) OVER (ORDER BY timestamp) AS "Cumulative Clones"',
    'FROM github_traffic',
    'WHERE $__timeFilter(timestamp)',
    '  AND repo_name IN ('
]
cumulative_query_lines.append('    ' + ', '.join(repo_names))
cumulative_query_lines.append('  )')
cumulative_query_lines.append('GROUP BY timestamp')
cumulative_query_lines.append('ORDER BY timestamp;')

cumulative_sql_query = '\n'.join(cumulative_query_lines)
print(cumulative_sql_query) 
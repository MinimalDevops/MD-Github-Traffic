import yaml

# Load the YAML file
with open('repos.yaml', 'r') as f:
    data = yaml.safe_load(f)

repos = data.get("repos", [])

# Start building the query
query_lines = [
    'SELECT',
    '  repo_name,',
    '  SUM(total_views) AS total_views,',
    '  SUM(total_clones) AS total_clones',
    'FROM github_traffic',
    'WHERE repo_name IN ('
]

# Add repo names to IN clause
repo_names = [f"'{r['owner']}/{r['repo']}'" for r in repos]
query_lines.append('    ' + ', '.join(repo_names))
query_lines.append(')')
query_lines.append('GROUP BY repo_name')
query_lines.append('ORDER BY total_views DESC;')

# Final query string
sql_query = '\n'.join(query_lines)
print(sql_query)

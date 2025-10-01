# GitHub Traffic Tracker

Track daily GitHub repository traffic (views and clones) and store metrics in Supabase (PostgreSQL/TimescaleDB).

Read the Blog: [How to Track GitHub Repo Traffic Beyond 14 Days](https://medium.com/@minimaldevops/how-to-track-github-repo-traffic-beyond-14-days-73d16c85129e)

## Features
- Fetches daily traffic metrics from GitHub REST API
- Stores metrics in Supabase (cloud Postgres) or a local database
- Visualizes metrics with Jupyter Notebook, Python script, or Grafana

## Why Supabase?
This project uses **Supabase** as a cloud-hosted PostgreSQL database. This means:
- Your data is **not tied to your local machine**—you won't lose metrics if you change laptops or work from multiple devices.
- You can always access your GitHub traffic history in the future.
- **Alternative:** You can use a local PostgreSQL database if you prefer, but you'll need to update the connection string in your `.env` and ensure your local DB is running when you run the scripts.

New to Supabase? [Learn how to setup Postgres here](https://docs.stacksync.com/guides/two-way-sync-salesforce-and-postgres/create-a-postgres-database-with-supabase-free-forever)

## Repository Configuration
Repositories to track are  configured in a separate `repos.yaml` file. Example:
```yaml
repos:
  - owner: MinimalDevops
    repo: MD-Youtube-Summarizer
  # - owner: another_owner
  #   repo: another_repo
```
You can add as many repositories as you like. The script will fetch metrics for all listed repos.

## Setup

### 1. GitHub Token
- Create a GitHub Personal Access Token (read-only scope)
- Add it to your `.env` file as `GITHUB_TOKEN`

#### Sample .env File
Create a `.env` file in your project root with the following content (replace the placeholder values with your actual credentials):

```
GITHUB_TOKEN=your_github_token_here
SUPABASE_HOST=your_supabase_host
SUPABASE_DB=your_database_name
SUPABASE_USER=your_db_user
SUPABASE_PASSWORD=your_db_password
SUPABASE_PORT=5432
```

### 2. Supabase/PostgreSQL Setup
- Create a Supabase project and database (or use a local PostgreSQL instance)
- Use the following SQL to create the table:

```sql
CREATE TABLE github_traffic (
    repo_name TEXT NOT NULL,
    timestamp DATE NOT NULL,
    unique_views INTEGER,
    total_views INTEGER,
    unique_clones INTEGER,
    total_clones INTEGER,
    PRIMARY KEY (repo_name, timestamp)
);
```

- Add your DB credentials to `.env`

### 3. Install Dependencies
All required packages (including Jupyter, pandas, matplotlib, plotly, PyYAML, etc.) are included in `requirements.txt`.

```bash
pip install -r requirements.txt
```
Or, if using [uv](https://github.com/astral-sh/uv):
```bash
uv pip install -r requirements.txt
```

### 4. Running the Script
- Edit `github_traffic_tracker.py` to add your repositories
- Run daily via cron or GitHub Actions
```bash
python github_traffic_tracker.py
```

## Automate Daily Fetch with Cron
To ensure you never miss a day of GitHub traffic data, set up a cronjob to run the tracker script automatically every day (e.g., at 9AM). This will keep your metrics up to date without manual intervention.

**Example cron line (runs daily at 9AM):**
```
0 9 * * * cd /path/to/your/project && /path/to/your/project/.venv/bin/python /path/to/your/project/github_traffic_tracker.py >> /path/to/your/project/cron.log 2>&1
```
- Adjust the paths as needed for your environment.
- This will log output to `cron.log` in your project directory.
- Use `crontab -e` to add the line to your crontab without removing existing jobs.

Automating the fetch ensures you always have the latest metrics, even if you forget to run the script manually.

---

## Visualization Options

### **A. Jupyter Notebook**
1. **Register your virtual environment as a Jupyter kernel:**
   ```bash
   python -m ipykernel install --user --name=github-traffic-venv --display-name "Python (github-traffic-venv)"
   ```
2. **(Recommended) Install the Jupyter extension in VSCode or your IDE** for best experience.
3. **Run Jupyter Notebook:**
   ```bash
   jupyter notebook
   ```
   - Open `visualize_metrics.ipynb` and run all cells.
   - Select the kernel named **Python (github-traffic-venv)**.
   - You'll see line plots for views and clones over time.
   - The notebook will plot all repositories by default. You can filter repos in the notebook by editing the code to select specific `repo_name` values.

### **B. Python Script**
1. **Run the provided script:**
   ```bash
   python visualize.py
   ```
   - This will display matplotlib plots for views and clones.
   - You can now filter which repository to plot using a command-line argument:
     ```bash
     python visualize.py --repo MinimalDevops/MD-Youtube-Summarizer
     ```
   - Omit `--repo` to plot all repos together.

### **C. Grafana Dashboard**
1. **Install Grafana:**
   - On macOS (Homebrew):
     ```bash
     brew install grafana
     brew services start grafana
     ```
   - Or see [Grafana Downloads](https://grafana.com/grafana/download) for other platforms.
2. **Open Grafana:**
   - Go to [http://localhost:3000](http://localhost:3000)
   - Login (default: `admin`/`admin`)
3. **Add PostgreSQL Data Source:**
   - Use your Supabase credentials (host, db, user, password, port, SSL required)
4. **Create a Dashboard:**
   - Generating Grafana Queries for Multiple Repos
      To easily generate a custom SQL query for your Grafana dashboard (with separate lines for each repo and metric), use the provided `grafana_query.py` script. This script reads your `repos.yaml` and outputs a SQL query tailored to your current repositories.
   ```bash
   python grafana_query.py
   ```
   - The script will print a SQL query to your terminal.
   - Copy and paste this query into your Grafana panel's query editor.
   - This will create separate lines for each repo's views and clones, with clear labels.

   **Benefit:**
   - No need to manually edit SQL for each new repo—just update `repos.yaml` and rerun the script.
   - Makes multi-repo dashboards easy and dynamic. 
   **Ensure:**
   - Set visualization to Time series/Line chart.
   - Adjust time range (top right) to include your data (e.g., "Last 30 days").

## Generating Grafana Queries

This project includes 3 Python scripts to generate different types of Grafana queries for your GitHub traffic data:

### 1. Individual Repository Time Series (`grafana_query.py`)
Generates time series queries for individual repositories with separate lines for each repo and metric.

```bash
python grafana_query.py
```

**What it does:**
- Creates separate lines for each repository's views and clones
- Shows time series data for each repo individually
- Perfect for line charts showing trends over time
- Each repo gets its own line in the visualization

**Use case:** When you want to see how each repository performs over time with separate trend lines.

### 2. All-Time Aggregated Totals (`grafana_aggregated_totals_query.py`)
Generates queries for all-time totals across all repositories combined.

```bash
python grafana_aggregated_totals_query.py
```

**What it does:**
- Shows total views and clones from the beginning until today
- Ignores the time range selected in Grafana
- Perfect for stat panels, gauges, or single value displays
- Gives you the grand total across all your repositories

**Use case:** When you want to show total traffic across all repositories as a single number (like a KPI card).

### 3. Per-Repository Breakdown (`grafana_total_count_query.py`)
Generates queries showing totals for each individual repository.

```bash
python grafana_total_count_query.py
```

**What it does:**
- Shows totals for each individual repository
- Great for table panels to see which repos perform best
- Allows you to compare repositories side by side
- Perfect for ranking repositories by traffic

**Use case:** When you want to see which repositories are your top performers in a table or bar chart format.

### How to Use These Queries

1. **Run the appropriate script** based on what you want to visualize
2. **Copy the generated SQL query** from the terminal output
3. **Paste it into your Grafana panel's query editor**
4. **Choose the right visualization type:**
   - Time series queries → Line charts, area charts
   - Aggregated totals → Stat panels, gauges, single value
   - Per-repo breakdown → Tables, bar charts

**Benefits:**
- Automatically includes all repositories from your `repos.yaml`
- No need to manually edit SQL when adding new repos
- Each script serves a different visualization need
- Easy to regenerate queries when your repo list changes

---

## Tips
- For Jupyter, ensure you select the correct Python kernel (your virtual environment) in VSCode or Jupyter Lab.
- If you have special characters in your DB password, URL-encode them in your `.env`.
- For Grafana, always check the time range and use Table view to debug queries.
- You can use a local PostgreSQL database instead of Supabase if you prefer, but your data will only be available on that machine.

---

## Upsert Logic (No Duplicates)
This project uses an upsert strategy when writing to the database:
- For each repository and day, the script attempts to insert a new row.
- If a row for the same `repo_name` and `timestamp` already exists, it is updated with the latest values from GitHub.
- This is achieved using the SQL statement:
  ```sql
  INSERT INTO github_traffic (...)
  VALUES (...)
  ON CONFLICT (repo_name, timestamp) DO UPDATE SET ...
  ```
- **Result:** No duplicate rows for the same repo and day, and your data is always up-to-date.

### Note on Date Filtering in Jupyter/Python
Unlike Grafana, the Jupyter notebook and Python script do **not** have built-in interactive date range filtering. If you want to plot data for a specific date range, you can filter the DataFrame in the code. For example:
```python
df = df[(df['timestamp'] >= '2025-06-01') & (df['timestamp'] <= '2025-06-03')]
```
Add this line before plotting to restrict the visualization to a certain date range.

### Troubleshooting Visualization Issues
- If your plot is empty or missing data:
  - Check the debug print output to see what data is being loaded and filtered.
  - Make sure your `--repo` argument (for the script) matches the repo name exactly, but note that filtering is now case- and whitespace-insensitive.
  - Check for leading/trailing spaces or case mismatches in repo names.
  - Use print statements to inspect the DataFrame content before plotting.
- If you only see a legend but no points, you may have only one data point or all values may be zero/NaN.
- For more than one data point, you can use line plots for a continuous view.

---

## License

This project is licensed under the [MIT License](LICENSE). You are free to use, modify, and distribute it as you wish.




import duckdb
import pandas as pd
import requests

# Fetch data from DataGolf API
API_KEY = "97a47cb8af3ce0af6a0e6a2a9e56"
url = f"https://feeds.datagolf.com/preds/get-dg-rankings?file_format=[ file_format ]&key={API_KEY}"

response = requests.get(url)
data = response.json()
print(data)

# Convert to DataFrame
df = pd.DataFrame(data["rankings"])

# Load data into DuckDB
con = duckdb.connect(database=":memory:")
con.execute("CREATE TABLE players AS SELECT * FROM df")

# Query DuckDB
result = con.execute("SELECT * FROM players WHERE datagolf_rank < 100").fetchdf()
print(result)

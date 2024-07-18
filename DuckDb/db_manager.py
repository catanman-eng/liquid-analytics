import duckdb
import pandas as pd

class DBManager:
    def __init__(self, db_file):
        self.db_file = db_file
        self.con = None

    def connect(self):
        self.con = duckdb.connect(database=self.db_file)
        return self.con

    def create_table(self,table_name, api_response):
        df = pd.DataFrame(api_response.json())  # noqa: F841
        self.con.execute(f"CREATE TABLE if not exists {table_name} as SELECT * FROM df")

    def query(self, query):
        return self.con.execute(query).fetchdf()

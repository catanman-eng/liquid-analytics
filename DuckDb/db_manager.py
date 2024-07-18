import duckdb

class DBManager:
    def __init__(self, db_file):
        self.db_file = db_file
        self.con = None

    def connect(self):
        self.con = duckdb.connect(database=self.db_file)

    def create_tables(self):
        create_players_table = """
        CREATE TABLE IF NOT EXISTS players (
            player_id INT,
            name VARCHAR,
            rank INT,
            strokes_gained_total FLOAT,
            country VARCHAR
            -- Add more columns as needed
        );
        """
        self.con.execute(create_players_table)

    def load_players_data(self, df_players):
        df_players.to_sql("players", self.con, index=False, if_exists="replace")

    def query(self, query):
        return self.con.execute(query).fetchdf()

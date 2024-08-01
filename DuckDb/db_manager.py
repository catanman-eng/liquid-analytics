import duckdb
import pandas as pd
import boto3

S3_BUCKET_NAME = "datagolf-api-duckdb"
S3_FILE_KEY = "datagolf_aws.db"
LOCAL_DB_FILE = "datagolf_aws.db"


class DBManager:
    def __init__(self):
        self.db_file = None
        self.con = None

    def connect(self):
        self.con = duckdb.connect(database=self.db_file)
        return self.con

    def create_table(self,table_name, api_response):
        df = pd.DataFrame(api_response.json())  # noqa: F841
        self.con.execute(f"CREATE TABLE if not exists {table_name} as SELECT * FROM df")

    def query(self, query):
        return self.con.execute(query).fetchdf()

    def download_db_from_s3(self):
        s3 = boto3.client("s3", region_name="ca-central-1")
        print(s3)
        s3.download_file("datagolf-api-duckdb", "datagolf_aws.db", LOCAL_DB_FILE)
        print(
            f"Downloaded {S3_FILE_KEY} from bucket {S3_BUCKET_NAME} to {LOCAL_DB_FILE}."
        )
        self.db_file = LOCAL_DB_FILE
        self.connect()

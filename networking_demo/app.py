from flask import Flask, jsonify
import psycopg2  # Use mysql.connector for MySQL
import boto3
import json
import os

app = Flask(__name__)

DB_HOST = os.getenv("DB_HOST")  
DB_NAME = os.getenv("DB_NAME") 


def get_db_connection(secret_name):
    client = boto3.client("secretsmanager")
    response = client.get_secret_value(SecretId=secret_name)
    secret = json.loads(response["SecretString"])

    username = secret["username"]
    password = secret["password"]

    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=username,
        password=password,
    )
    return conn


@app.route("/")
def index():
    return "Welcome to my Flask API!"


@app.route("/data", methods=["GET"])
def get_data():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * CURRENT_TIMESTAMP;")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(rows)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)

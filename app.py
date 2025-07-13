import os

import dash
import duckdb
import plotly.express as px
from dash import dcc, html
from dotenv import load_dotenv

load_dotenv()

# Default to 'production' unless explicitly set to 'development' in .env
APP_ENV = os.getenv("APP_ENV", "prod")


def get_db_connection():
    """Establishes a connection to DuckDB based on the environment."""

    if APP_ENV == "dev":
        # For local dev, use localhost for port-forwarding
        pg_host = "localhost"
        s3_endpoint = "http://localhost:9000"
    else:
        # In production, use in-cluster Kubernetes service names
        pg_host = "postgres.ducklake.svc.cluster.local"
        s3_endpoint = "http://minio-svc.ducklake.svc.cluster.local:9000"

    # Get credentials from environment (works for both .env and k8s secrets)
    pg_user = os.getenv("POSTGRES_USER")
    pg_password = os.getenv("POSTGRES_PASSWORD")
    pg_db = os.getenv("POSTGRES_DB")
    s3_access_key = os.getenv("MINIO_ROOT_USER")
    s3_secret_key = os.getenv("MINIO_ROOT_PASSWORD")
    data_path = "s3://ducklake/data"

    if not all([pg_user, pg_password, pg_db, s3_access_key, s3_secret_key]):
        raise ValueError("Database or S3 credentials are not set.")

    try:
        # Connect and configure S3 access for DuckDB
        con = duckdb.connect()
        con.execute(f"SET s3_endpoint='{s3_endpoint.split('//')[1]}';")
        con.execute(f"SET s3_access_key_id='{s3_access_key}';")
        con.execute(f"SET s3_secret_access_key='{s3_secret_key}';")
        con.execute("SET s3_url_style='path';")
        con.execute("SET s3_use_ssl=false;")

        # Construct DSN and ATTACH command
        dsn = f"dbname={pg_db} user={pg_user} password={pg_password} host={pg_host} port=5433"
        attach_sql = f"ATTACH 'ducklake:postgres:{dsn}' AS prod_lake (DATA_PATH '{data_path}', READ_ONLY);"

        con.execute("INSTALL ducklake; LOAD ducklake;")
        con.execute(attach_sql)
        con.execute("USE prod_lake;")
        return con
    except duckdb.IOException as e:
        print("\n--- CONNECTION FAILED ---")
        print(f"Error: {e}")
        print("\nHint: If you are running locally for development, ensure you have:")
        print("  1. Set 'APP_ENV=dev' in your .env file.")
        print(
            "  2. Started the 'kubectl port-forward' commands for Postgres and MinIO."
        )
        print("-------------------------\n")
        raise  # Re-raise the exception to stop the app


def get_iris_data():
    con = get_db_connection()
    df = con.execute("SELECT * FROM dev_data.iris").fetchdf()
    con.close()
    return df


app = dash.Dash(__name__)
server = app.server

df = get_iris_data()

app.layout = html.Div(
    [
        html.H1("DuckLake Iris Dataset Dashboard"),
        dcc.Graph(
            id="sepal-length-vs-width",
            figure=px.scatter(
                df, x="sepal width (cm)", y="sepal length (cm)", color="species"
            ),
        ),
    ]
)

if __name__ == "__main__":
    app.run(debug=APP_ENV == "dev", host="0.0.0.0", port=8050)

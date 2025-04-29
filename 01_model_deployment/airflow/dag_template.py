import os
import requests
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.hooks.base import BaseHook

# DAG configuration
default_args = {
    "owner": "airflow",
    "start_date": datetime(2025, 1, 1),
    "retries": 1,
}

dag = DAG(
    "optimized_data_pipeline",
    default_args=default_args,
    schedule_interval="@monthly",  # Runs on the first day of each month
    catchup=False,  # Important to prevent backfilling
    max_active_runs=1,  # Ensures only one run at a time
)


def get_db_connection(conn_id="postgres_default"):
    """Retrieves PostgreSQL credentials from Airflow connections"""
    conn = BaseHook.get_connection(conn_id)
    return {
        "url": f"postgresql://{conn.login}:{conn.password}@{conn.host}:{conn.port}/{conn.schema}",
        "engine": create_engine(
            f"postgresql://{conn.login}:{conn.password}@{conn.host}:{conn.port}/{conn.schema}"
        ),
    }


def validate_file_path(file_path):
    """Validates that file exists and is accessible"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    if not os.access(file_path, os.R_OK):
        raise PermissionError(f"No read access to file: {file_path}")


def load_data(file_path):
    """Loads CSV file with validation"""
    validate_file_path(file_path)
    return pd.read_csv(file_path)


def save_data(dataframe, table_name, connection):
    """Saves DataFrame to PostgreSQL with optimized method"""
    with connection["engine"].begin() as conn:  # Automatic transaction
        dataframe.to_sql(
            name=table_name,
            con=conn,
            if_exists="replace",
            index=False,
            method="multi",  # Faster bulk insert
            chunksize=1000,
        )


def merge_datasets(**context):
    """Merges aircraft, flight, and airport data"""
    # Load all required datasets
    datasets = {
        "aircraft": load_data("/data/aircraft_data.csv"),
        "flights": load_data("/data/flight_data.csv"),
        "airports": load_data("/data/airport_data.csv"),
    }

    # Perform merges
    merged_data = (
        datasets["flights"]
        .merge(datasets["aircraft"], on="aircraft_id", how="left")
        .merge(datasets["airports"], on="airport_id", how="left")
    )

    # Save results
    db_conn = get_db_connection()
    save_data(merged_data, "merged_flight_data", db_conn)
    merged_data.to_csv("/data/merged_data.csv", index=False)

    return merged_data.shape  # Return shape for logging


def generate_predictions(**context):
    """Generates predictions using FastAPI endpoint"""
    # Load merged data
    merged_data = load_data("/data/merged_data.csv")

    # Get API connection details
    api_conn = BaseHook.get_connection("fastapi_service")
    endpoint = f"{api_conn.host}/predict_impact"
    auth = (api_conn.login, api_conn.password) if api_conn.login else None

    # Batch prediction request
    response = requests.post(
        endpoint,
        json=merged_data.to_dict(orient="records"),
        auth=auth,
        timeout=30,  # Add timeout
    )

    if response.status_code != 200:
        raise ValueError(f"API request failed: {response.text}")

    # Process and save predictions
    predictions = pd.DataFrame(response.json())
    db_conn = get_db_connection()
    save_data(predictions, "flight_predictions", db_conn)
    predictions.to_csv("/data/predictions.csv", index=False)

    return predictions.shape  # Return shape for logging


# Define tasks
merge_task = PythonOperator(
    task_id="merge_datasets",
    python_callable=merge_datasets,
    dag=dag,
    execution_timeout=timedelta(minutes=30),
)  # Add timeout

predict_task = PythonOperator(
    task_id="generate_predictions",
    python_callable=generate_predictions,
    dag=dag,
    execution_timeout=timedelta(minutes=30),
)

# Set dependencies
merge_task >> predict_task

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import pandas as pd
import os

# DAG configuration
default_args = {
    "owner": "airflow",
    "start_date": datetime(2025, 1, 1),
    "retries": 1,
}

dag = DAG(
    "data_ingestion_pipeline_on_premise",
    default_args=default_args,
    schedule_interval="0 0 1 * *",  # Runs on the first day of each month at midnight
)


# Function to fetch data from local files
def fetch_data_from_local(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")
    return pd.read_csv(file_path)


# Function to merge data
def merge_data():
    # Load data
    aircraft_data = fetch_data_from_local("/data/aircraft_data.csv")
    flight_data = fetch_data_from_local("/data/flight_data.csv")
    airport_data = fetch_data_from_local("/data/airport_data.csv")

    # Merge data (simple example with a common key)
    merged_data = pd.merge(flight_data, aircraft_data, on="aircraft_id")
    merged_data = pd.merge(merged_data, airport_data, on="airport_id")

    # Save merged data
    merged_data.to_csv("/data/merged_data.csv", index=False)
    print("Merged data saved to /data/merged_data.csv")


# Airflow tasks
fetch_aircraft_data = PythonOperator(
    task_id="fetch_aircraft_data",
    python_callable=lambda: fetch_data_from_local("/data/aircraft_data.csv"),
    dag=dag,
)

fetch_flight_data = PythonOperator(
    task_id="fetch_flight_data",
    python_callable=lambda: fetch_data_from_local("/data/flight_data.csv"),
    dag=dag,
)

fetch_airport_data = PythonOperator(
    task_id="fetch_airport_data",
    python_callable=lambda: fetch_data_from_local("/data/airport_data.csv"),
    dag=dag,
)

merge_data_task = PythonOperator(
    task_id="merge_data",
    python_callable=merge_data,
    dag=dag,
)

# Define task dependencies
[fetch_aircraft_data, fetch_flight_data, fetch_airport_data] >> merge_data_task

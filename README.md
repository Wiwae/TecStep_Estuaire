# Estuaire - Aerospace Data Scientist Challenge

This repo contains my answer to the proposed challenge. It includes several parts:
- *00_data_exploration* : folder containing the EDA jupyter notebook, and associated utils files
- *01_model_deployment* : folder containing the required files for the chosen model deployment with FastAPI. It also contains a template of automation file with Apache Airflow (that has not been tested), and an (empty) test folder.
- *Dockerfile* : file to build the image of the FastAPI service
- *pyproject.toml* : file containing the needed environment description to run the code


## Requirements

This project runs with uv for purposes of packages managements. If uv is not installed yet, run (for linux):

```
curl -LsSf https://astral.sh/uv/install.sh | sh
```

For installation on Mac or Windows, see : https://docs.astral.sh/uv/getting-started/installation/


Once uv is installed, install the environment:

```
uv sync
```

## Running the notebook

Make sure to choose the new *.venv/bin/python* environment to run the code.

## Running the model (FastAPI service)

Once in the *app* folder, choose a port (here 80) to expose the service and run:

```
uv run uvicorn main:app --host 0.0.0.0 --port 80
```

Then, you will be able to make inference from a client using http requests.

## Build the Docker image:

The Dockerfile contains the layers to build an image of the inference service using FastAPI. First, build the image with:

```
docker build -t inference_service . 
```

And to run your container, choosing a new port MY_PORT of your machine to map the container port:

```
docker run -d -p MY_PORT:80 inference_service
```

Or to run it interactively:

```
docker run -i inference_service
```

## About the inference architecture

The proposed architecture is thought for an On-Premise use, but it can be adapted for Cloud use by replacing services by their equivalent in a proprietary environment (eg AWS).

The global schema is:

![alt text](Estuaire.drawio(1).png)

I assumed that input sources are given, each at some point for the month, as csv files, that are stored locally on the server.

To run the automation of the ETL, I chose to use Apache Airflow (with a template file in *01_model_deployment/airflow*), that allows to chose the frequency of the runs (at the beginning of each month, processing the data that arrived during the previous 30 days), and their order (fetch and merge -and store-, then infer -and store-).

The inference is made using the *FastAPI* interface, that is serving the best trained *XGboost* model, by *http* requests.

All the data is stored in a PostGRESQL Database (for instance using one only table, as the one provided in data_challenge.csv), with which we communicate through the *sqlachemy* python library.

The computed values are thus available in the database.

**Adapting to cloud use:**

One can adapt the architecture to deploy on the cloud, by switching the services. For instance, on AWS:

- FastAPI <- SageMaker
- PostGRESQL DB, and source files that are stored locally <- Amazon S3 Bucket
- Apache Airflow <- Amazon Step Functions or AWS Glue



## Bonus

Some use cases for this product :
- provide an API to use the trained model
- analytics software for decision makers in Airlines or governments
- ...


To improve the model, i would:
- evaluate more the data quality, make sure data is as clean as possible (sharpen feature selection and entry selection)
- add data
  - add trajectory precisions (flight altitudes, GNSS locations...)
  - add weather data
  - complete aircraft info (type of fuel, state...)
  - ...
- try other models (more complex ones?)

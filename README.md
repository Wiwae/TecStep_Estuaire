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

## About the inference architecture

The proposed architecture is thought for an On-Premise use, but it can be adapted for Cloud use by replacing services by their equivalent in a proprietary environment (eg AWS).

The global schema is:

![alt text](Estuaire.drawio(1).png)
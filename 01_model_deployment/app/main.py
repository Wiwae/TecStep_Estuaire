from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import numpy as np
from xgboost import XGBRegressor

# Initialize app
app = FastAPI()

# Load the chosen model (here XGBoost)
model: XGBRegressor = joblib.load("../model/xgboost_model.pkl")


# Pydantic model for request body
class Features(BaseModel):
    input_features: list


@app.post("/predict")
def predict(data: Features):
    # Prepare data for prediction
    features = np.array(data.input_features).reshape(1, -1)
    # Run the inferance
    prediction = model.predict(features)
    return {"prediction": prediction.tolist()}

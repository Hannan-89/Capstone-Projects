from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import joblib
import uvicorn
from typing import Optional

from fastapi.middleware.cors import CORSMiddleware

# Initialize FastAPI app
app = FastAPI(title="Chronic Kidney Disease Prediction API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model and metadata
try:
    model = joblib.load('model.joblib')
    metadata = joblib.load('metadata.joblib')
except Exception as e:
    print(f"Error loading model or metadata: {e}")
    model = None
    metadata = None

# Define input schema
class CKDInput(BaseModel):
    age: Optional[float] = None
    bp: Optional[float] = None
    sg: Optional[float] = None
    al: Optional[float] = None
    su: Optional[float] = None
    rbc: Optional[str] = None
    pc: Optional[str] = None
    pcc: Optional[str] = None
    ba: Optional[str] = None
    bgr: Optional[float] = None
    bu: Optional[float] = None
    sc: Optional[float] = None
    sod: Optional[float] = None
    pot: Optional[float] = None
    hemo: Optional[float] = None
    pcv: Optional[float] = None
    wc: Optional[float] = None
    rc: Optional[float] = None
    htn: Optional[str] = None
    dm: Optional[str] = None
    cad: Optional[str] = None
    appet: Optional[str] = None
    pe: Optional[str] = None
    ane: Optional[str] = None

@app.get("/")
def read_root():
    return {"message": "Welcome to the CKD Prediction API. Use /docs for documentation."}

@app.post("/predict")
def predict(data: CKDInput):
    if model is None or metadata is None:
        raise HTTPException(status_code=500, detail="Model not loaded. Please run train_model.py first.")
    
    # Convert input to DataFrame
    input_dict = data.dict()
    df_input = pd.DataFrame([input_dict])

    # Preprocessing
    # 1. Fill missing values using metadata
    for col, val in metadata['impute_values'].items():
        if col in df_input.columns:
            df_input[col] = df_input[col].fillna(val)

    # 2. One-hot encoding
    # We use pd.get_dummies and then reindex to match training columns
    df_encoded = pd.get_dummies(df_input, columns=metadata['categorical_features'], drop_first=True)
    
    # Ensure all columns from training are present
    for col in metadata['final_columns']:
        if col not in df_encoded.columns:
            df_encoded[col] = 0
            
    # Align column order
    df_encoded = df_encoded[metadata['final_columns']]

    # Prediction
    prediction = model.predict(df_encoded)[0]
    result = metadata['target_map'][prediction]

    return {
        "prediction": result,
        "prediction_code": int(prediction)
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

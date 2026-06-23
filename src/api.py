from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from datetime import datetime

app = FastAPI(
    title="GH-Yield API",
    description="Ghana 91-Day Treasury Bill Rate Forecasting System",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_PATH = Path(__file__).parent.parent / "data"


def get_prediction():
    saved = joblib.load(DATA_PATH / "model.joblib")
    model = saved["model"]
    features = saved["features"]
    df = pd.read_csv(DATA_PATH / "features_dataset.csv", parse_dates=["date"])
    latest = df.iloc[-1]
    X = latest[features].values.reshape(1, -1)
    predicted = float(model.predict(X)[0])
    current = float(latest["tbill_91"])
    change = predicted - current
    if change < -0.5:
        signal = "BUY"
    elif change > 0.5:
        signal = "WAIT"
    else:
        signal = "HOLD"
    return {
        "date": str(latest["date"]),
        "current_rate": round(current, 2),
        "predicted_next_month": round(predicted, 2),
        "predicted_change": round(change, 2),
        "signal": signal
    }


@app.get("/")
def root():
    return {
        "project": "GH-Yield",
        "description": "Ghana T-Bill Rate Forecasting API",
        "endpoints": ["/predict", "/signal", "/health", "/history"]
    }


@app.get("/predict")
def predict():
    return get_prediction()


@app.get("/signal")
def signal():
    result = get_prediction()
    if result["signal"] == "BUY":
        result["recommendation"] = f"Lock in the current {result['current_rate']}% rate. Model predicts decline."
    elif result["signal"] == "WAIT":
        result["recommendation"] = f"Hold cash. Model predicts rates will rise to {result['predicted_next_month']}%."
    else:
        result["recommendation"] = "Maintain current position. No significant change expected."
    result["timestamp"] = datetime.now().isoformat()
    return result


@app.get("/health")
def health():
    try:
        saved = joblib.load(DATA_PATH / "model.joblib")
        return {
            "status": "healthy",
            "model_loaded": True,
            "n_features": len(saved["features"]),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


@app.get("/history")
def history():
    df = pd.read_csv(DATA_PATH / "ghana_tbill_rates.csv", parse_dates=["date"])
    df["date"] = df["date"].dt.strftime("%Y-%m-%d")
    return df.to_dict(orient="records")

# backend/main.py
from feature_engineering import transform_openaq_to_features


import os, json
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import joblib
import numpy as np
from fastapi.middleware.cors import CORSMiddleware
import requests

BASE_DIR = os.path.dirname(__file__)
MODEL_DIR = os.path.join(BASE_DIR, "model")

# Load models and metadata
rf = joblib.load(os.path.join(MODEL_DIR, "model_rf.joblib"))
clf_rf = joblib.load(os.path.join(MODEL_DIR, "model_clf_rf.joblib"))
with open(os.path.join(MODEL_DIR, "metadata.json")) as f:
    META = json.load(f)
FEATURE_ORDER = META["features"]
LABELS = META.get("label_mapping", None)

app = FastAPI(title="AQI Predict Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class FeaturePayload(BaseModel):
    features: dict  # e.g. {"si": 10, "ni": 2.8, "rpi": 17}

def categorize_aqi(aqi: float) -> str:
    # same bins used in your notebook
    if aqi <= 50:
        return 'Good'
    elif aqi <= 100:
        return 'Moderate'
    elif aqi <= 200:
        return 'Poor'
    elif aqi <= 300:
        return 'Unhealthy'
    elif aqi <= 400:
        return 'Very Unhealthy'
    else:
        return 'Hazardous'

def health_advisory(category: str) -> str:
    c = category.lower()
    if c == 'good':
        return 'Air quality is satisfactory. Normal outdoor activities are safe.'
    if c == 'moderate':
        return 'Sensitive individuals (asthma, COPD) should limit prolonged outdoor exertion.'
    if c == 'poor':
        return 'Unhealthy for sensitive groups. Consider wearing a mask and reducing outdoor time.'
    if c == 'unhealthy':
        return 'Everyone may begin to experience health effects. Avoid outdoor exertion; sensitive groups should stay indoors.'
    if c == 'very unhealthy':
        return 'Health alert: serious effects possible. Stay indoors, use air purifiers if available.'
    return 'Emergency conditions. Avoid all outdoor activities; seek cleaner indoor air.'

@app.post("/predict")
def predict(payload: FeaturePayload):
    feat = payload.features
    # ensure correct ordered vector
    try:
        x = [float(feat[k]) for k in FEATURE_ORDER]
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"missing feature {e}")
    x_arr = np.array([x])

    # regression prediction
    aqi_pred = float(rf.predict(x_arr)[0])
    aqi_category = categorize_aqi(aqi_pred)

    # classification prediction
    class_pred = clf_rf.predict(x_arr)[0]
    # your classifier already predicts labels like 'Good' etc. If it predicts numeric classes,
    # use LABELS mapping; otherwise return as-is.
    if isinstance(class_pred, (int, float)) and LABELS:
        class_label = LABELS[int(class_pred)]
    else:
        class_label = str(class_pred)

    return {
        "aqi_regression": round(aqi_pred, 2),
        "aqi_reg_category": aqi_category,
        "aqi_classification_label": class_label,
        "feature_order_used": FEATURE_ORDER,
        "advisory": health_advisory(aqi_category)
    }

@app.get("/meta")
def meta():
    return {"features": FEATURE_ORDER, "labels": LABELS}

@app.get("/predict_by_openaq")
def predict_by_openaq(city: str = Query(..., description="City name as per OpenAQ"),
                      country: str = Query("IN", description="ISO country code, e.g., IN, US"),
                      lookback_hours: int = Query(6, ge=1, le=48)):
    """
    Fetch latest PM2.5, NO2, PM10 measurements via OpenAQ v2 for the given city/country,
    map to features, and run predictions.
    """
    try:
        url = "https://api.openaq.org/v2/measurements"
        params = {
            "city": city,
            "country": country,
            "parameter": ["pm25", "no2", "pm10"],
            "limit": 200,
            "order_by": "datetime",
            "sort": "desc"
        }
        resp = requests.get(url, params=params, timeout=15)
        if resp.status_code != 200:
            raise HTTPException(status_code=502, detail=f"OpenAQ error: {resp.status_code}")
        data = resp.json()
        results = data.get("results", [])
        features = transform_openaq_to_features(results, lookback_hours=lookback_hours)
        # Predict with existing endpoint logic
        x = [float(features[k]) for k in FEATURE_ORDER]
        x_arr = np.array([x])
        aqi_pred = float(rf.predict(x_arr)[0])
        aqi_category = categorize_aqi(aqi_pred)
        class_pred = clf_rf.predict(x_arr)[0]
        if isinstance(class_pred, (int, float)) and LABELS:
            class_label = LABELS[int(class_pred)]
        else:
            class_label = str(class_pred)
        return {
            "city": city,
            "country": country,
            "features": features,
            "aqi_regression": round(aqi_pred, 2),
            "aqi_reg_category": aqi_category,
            "aqi_classification_label": class_label,
            "advisory": health_advisory(aqi_category)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

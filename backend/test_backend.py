import pytest
import os
import sys
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from main import app, categorize_aqi, health_advisory, hvac_throttling_recommendation

client = TestClient(app)

def test_health_check():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"
    assert "models_loaded" in res.json()

def test_meta():
    res = client.get("/meta")
    assert res.status_code == 200
    assert "features" in res.json()
    assert res.json()["features"] == ["si", "ni", "rpi"]

def test_predict_manual():
    payload = {"features": {"si": 45.0, "ni": 32.0, "rpi": 95.0}}
    res = client.post("/predict", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "aqi_regression" in data
    assert "aqi_reg_category" in data
    assert "advisory" in data
    assert "hvac_throttling_policy" in data

def test_predict_by_openaq_fallback():
    # Calling predict_by_openaq for Delhi should return 200 with fallback if OpenAQ is unreachable
    res = client.get("/predict_by_openaq?city=Delhi&country=IN")
    assert res.status_code == 200
    data = res.json()
    assert data["city"] == "Delhi"
    assert "aqi_regression" in data
    assert "telemetry_source" in data

def test_hvac_throttling():
    low_aqi = hvac_throttling_recommendation(45.0)
    assert low_aqi["mode"] == "OPTIMAL_FRESH_AIR"
    assert low_aqi["damper_intake_percent"] == 100

    high_aqi = hvac_throttling_recommendation(350.0)
    assert high_aqi["mode"] == "EMERGENCY_ISOLATION"
    assert high_aqi["damper_intake_percent"] <= 20

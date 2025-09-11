import pandas as pd
import requests
import numpy as np

# ===== Load your CSV with proper encoding =====
df = pd.read_csv("data.csv", encoding="latin1",low_memory=False)  # change to ISO-8859-1 if needed



# Clean up column names (strip spaces if any)
df.columns = [c.strip().lower() for c in df.columns]

# Pick the first valid row
row = df.iloc[0]

# Extract values
pm25 = row.get("pm2_5", np.nan)
no2 = row.get("no2", np.nan)
pm10 = row.get("spm", np.nan)   # treating SPM as PM10 proxy

# Handle "NA" strings and missing values
def to_float(val):
    try:
        if str(val).upper() == "NA":
            return np.nan
        return float(val)
    except:
        return np.nan

pm25 = to_float(pm25)
no2 = to_float(no2)
pm10 = to_float(pm10)

# Fallbacks if missing
if np.isnan(pm25):
    pm25 = 0.0
if np.isnan(no2):
    no2 = 0.0
if np.isnan(pm10):
    pm10 = 0.0

features = {"si": pm25, "ni": no2, "rpi": pm10}
print("✅ Features extracted:", features)

# ===== Call your backend API =====
response = requests.post("http://127.0.0.1:8080/predict", json={"features": features})

if response.status_code != 200:
    print("❌ Error calling /predict:", response.status_code, response.text)
else:
    print("📊 Prediction response:", response.json())

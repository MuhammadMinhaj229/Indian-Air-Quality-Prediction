# backend/test_transform.py
from feature_engineering import transform_openaq_to_features
from datetime import datetime, timezone, timedelta

# build a small fake OpenAQ 'results' list
now_str = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
sample = [
    {"parameter":"pm25", "value": 95, "date": {"utc": now_str}},
    {"parameter":"no2",  "value": 34, "date": {"utc": now_str}},
    {"parameter":"pm10", "value": 140, "date": {"utc": now_str}}
]

print("sample measurements:", sample)
features = transform_openaq_to_features(sample, lookback_hours=6)
print("mapped features:", features)

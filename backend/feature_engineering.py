# backend/feature_engineering.py
"""
Transform OpenAQ measurement results into the three features your model expects:
  - si  <- mapped from PM2.5 (pm25)
  - ni  <- mapped from NO2  (no2)
  - rpi <- mapped from PM10 (pm10)
This version fixes timezone-aware datetime handling.
"""

from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any

def _parse_openaq_time(tstr: str):
    """Parse OpenAQ UTC timestamp like '2025-09-09T08:00:00Z' -> timezone-aware datetime (UTC)."""
    if not tstr:
        return None
    try:
        # Convert trailing 'Z' to '+00:00' so fromisoformat can parse timezone
        if tstr.endswith("Z"):
            tstr = tstr.replace("Z", "+00:00")
        dt = datetime.fromisoformat(tstr)
        # if dt has no tzinfo (naive), assume UTC
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        # fallback: try parsing date portion only and mark UTC
        try:
            dt = datetime.strptime(tstr.split("T")[0], "%Y-%m-%d")
            return dt.replace(tzinfo=timezone.utc)
        except Exception:
            return None

def _avg_measurements(measurements: List[Dict[str, Any]], parameter: str, lookback_hours: int = 6):
    """
    Compute mean of `parameter` values in `measurements` within lookback_hours.
    measurements: list of OpenAQ result dicts (each with 'parameter','value','date').
    """
    now = datetime.now(timezone.utc)          # timezone-aware UTC
    vals = []
    param_lower = parameter.lower()
    for m in measurements:
        if m.get('parameter', '').lower() != param_lower:
            continue
        date_info = m.get('date', {})
        # OpenAQ often returns {'utc': '...', 'local': '...'}
        tstr = None
        if isinstance(date_info, dict):
            tstr = date_info.get('utc') or date_info.get('local')
        else:
            tstr = m.get('date')
        t = _parse_openaq_time(tstr) if isinstance(tstr, str) else None
        if t:
            # both now and t are timezone-aware (UTC)
            if (now - t) > timedelta(hours=lookback_hours):
                continue
        v = m.get('value')
        if v is None:
            continue
        try:
            vals.append(float(v))
        except Exception:
            continue
    if not vals:
        return None
    return sum(vals) / len(vals)

def transform_openaq_to_features(measurements: List[Dict[str, Any]],
                                 lookback_hours: int = 6,
                                 pm25_to_si_factor: float = 1.0,
                                 no2_to_ni_factor: float = 1.0,
                                 pm10_to_rpi_factor: float = 1.0) -> Dict[str, float]:
    """
    Map OpenAQ 'results' list -> feature dict {"si","ni","rpi"}.
    """
    pm25 = _avg_measurements(measurements, "pm25", lookback_hours)
    no2  = _avg_measurements(measurements, "no2", lookback_hours)
    pm10 = _avg_measurements(measurements, "pm10", lookback_hours)

    si = pm25 * pm25_to_si_factor if pm25 is not None else None
    ni = no2  * no2_to_ni_factor if no2  is not None else None
    rpi = pm10 * pm10_to_rpi_factor if pm10 is not None else None

    # sensible fallbacks
    if si is None and rpi is not None:
        si = rpi
    if rpi is None and si is not None:
        rpi = si
    if ni is None:
        ni = 0.0

    si = float(si if si is not None else 0.0)
    ni = float(ni if ni is not None else 0.0)
    rpi = float(rpi if rpi is not None else 0.0)

    return {"si": si, "ni": ni, "rpi": rpi}

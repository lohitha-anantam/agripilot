import requests
from datetime import datetime, timezone

def fetch_weather(latitude, longitude):
    """Fetch Open-Meteo daily forecast. No API key required; graceful fallback on errors."""
    try:
        url="https://api.open-meteo.com/v1/forecast"
        params={"latitude":latitude,"longitude":longitude,
                "daily":"precipitation_sum,temperature_2m_max",
                "forecast_days":2,"timezone":"auto"}
        response=requests.get(url,params=params,timeout=10)
        response.raise_for_status()
        daily=response.json().get("daily",{})
        rain=daily.get("precipitation_sum",[])
        temps=daily.get("temperature_2m_max",[])
        return {"ok":True,"rain_24h_mm":float(rain[0]) if rain else None,
                "rain_next_24h_mm":float(rain[0]) if rain else 0.0,
                "max_temp_c":float(temps[0]) if temps else None,
                "source":"Open-Meteo forecast"}
    except Exception as exc:
        return {"ok":False,"error":str(exc),"source":"Unavailable"}

"""
J.A.R.V.I.S. — Environmental & Weather Intelligence Skill (Phase 7)
Retrieves live local weather and atmospheric conditions without API keys.
Includes offline fallback with authentic J.A.R.V.I.S. dialogue.
"""

import requests
from typing import Dict, Any, Tuple, Optional

from core.responses import get_response
from skills.web_search import check_internet_connection
import config

WEATHER_URL = "https://wttr.in/?format=j1"
HEADERS = {"User-Agent": "curl/7.68.0"}


def get_current_weather(location: Optional[str] = None) -> Tuple[bool, Dict[str, Any], str]:
    """
    Fetches real-time weather data.
    Returns (success_bool, data_dict, summary_message).
    """
    if not check_internet_connection():
        return False, {}, "Environmental sensors report internet connectivity is currently offline, sir."

    url = f"https://wttr.in/{location}?format=j1" if location else WEATHER_URL

    try:
        resp = requests.get(url, headers=HEADERS, timeout=4.0)
        if resp.status_code != 200:
            return False, {}, "Unable to contact meteorological servers at this time, sir."

        data = resp.json()
        curr = data.get("current_condition", [{}])[0]
        temp_c = curr.get("temp_C", "N/A")
        temp_f = curr.get("temp_F", "N/A")
        desc = curr.get("weatherDesc", [{}])[0].get("value", "Clear")
        humidity = curr.get("humidity", "N/A")
        wind_kmh = curr.get("windspeedKmph", "N/A")
        wind_dir = curr.get("winddir16Point", "")

        # Nearest area name if available
        area = "your current location"
        nearest = data.get("nearest_area", [{}])
        if nearest:
            area_names = nearest[0].get("areaName", [{}])
            if area_names:
                area = area_names[0].get("value", area)

        weather_dict = {
            "temp_c": temp_c,
            "temp_f": temp_f,
            "condition": desc,
            "humidity": humidity,
            "wind_kmh": wind_kmh,
            "wind_dir": wind_dir,
            "location": area
        }

        summary = (
            f"Meteorological telemetry for {area} indicates {desc.lower()} with a temperature of "
            f"{temp_c} degrees Celsius, humidity at {humidity} percent, and winds from the {wind_dir} "
            f"at {wind_kmh} kilometers per hour, sir."
        )

        return True, weather_dict, summary

    except Exception as e:
        return False, {}, f"Meteorological data acquisition failed: {e}"


def handle_weather_query(intent_res) -> str:
    loc = intent_res.parameters.get("location")
    success, data, msg = get_current_weather(location=loc)
    return msg


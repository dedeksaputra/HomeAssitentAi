import json
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


get_weather_tool = {
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": (
            "Mengambil cuaca terkini berdasarkan nama kota. "
            "Gunakan saat user menanyakan cuaca atau suhu."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "Nama kota, misalnya Jakarta atau Bandung."
                }
            },
            "required": ["city"]
        }
    }
}


WEATHER_URL = "https://wttr.in/{city}?format=j1"


def get_weather(city: str) -> dict:
    """Mengambil cuaca terkini dari wttr.in."""
    city = str(city or "").strip()
    if not city:
        return {
            "success": False,
            "message": "Nama kota tidak boleh kosong."
        }

    request = Request(
        WEATHER_URL.format(city=quote(city)),
        headers={"User-Agent": "HomeAssisten/1.0"},
    )

    try:
        with urlopen(request, timeout=10) as response:
            data = json.load(response)
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as error:
        return {
            "success": False,
            "message": f"Data cuaca tidak dapat diambil: {error}"
        }

    try:
        current = data["current_condition"][0]
        location = data["nearest_area"][0]
        area = location["areaName"][0]["value"]
        country = location["country"][0]["value"]
        description = current["weatherDesc"][0]["value"]
        return {
            "success": True,
            "city": area,
            "country": country,
            "condition": description,
            "temperature_c": current["temp_C"],
            "feels_like_c": current["FeelsLikeC"],
            "humidity_percent": current["humidity"],
            "wind_kmh": current["windspeedKmph"],
        }
    except (KeyError, IndexError, TypeError) as error:
        return {
            "success": False,
            "message": f"Format data cuaca tidak dikenali: {error}"
        }

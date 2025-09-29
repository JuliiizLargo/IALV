import os
import requests

SERP_API_KEY = os.getenv("SERPAPI_API_KEY")
BASE_URL = "https://serpapi.com/search.json"

DEFAULT_TIMEOUT = 15

class SerpApiError(Exception):
    pass

def _ensure_api_key():
    if not SERP_API_KEY:
        raise SerpApiError("SERPAPI_API_KEY no configurada")

def _get(params: dict):
    _ensure_api_key()
    try:
        r = requests.get(BASE_URL, params=params, timeout=DEFAULT_TIMEOUT)
        r.raise_for_status()
        data = r.json()
        # SerpAPI suele incluir 'error' en JSON cuando algo falla con 200
        if isinstance(data, dict) and data.get("error"):
            raise SerpApiError(data["error"]) 
        return data
    except requests.Timeout as e:
        raise SerpApiError("Timeout comunicando con SerpAPI") from e
    except requests.RequestException as e:
        raise SerpApiError(f"Error HTTP SerpAPI: {e}") from e

def search_hotels(city: str):
    params = {"engine": "google_hotels", "q": city, "api_key": SERP_API_KEY}
    data = _get(params)
    # Intentar extraer un resumen compacto
    results = []
    for item in (data.get("properties") or [])[:5]:
        results.append({
            "name": item.get("name"),
            "rating": item.get("rating"),
            "price": item.get("extracted_price") or item.get("rate_per_night"),
            "link": item.get("link") or item.get("booking_link"),
        })
    return results or data

def search_flights(origin: str, destination: str, date: str):
    params = {
        "engine": "google_flights",
        "departure_id": origin,
        "arrival_id": destination,
        "outbound_date": date,
        "api_key": SERP_API_KEY,
    }
    data = _get(params)
    flights = []
    for f in (data.get("best_flights") or [])[:3]:
        price = f.get("price")
        legs = f.get("legs") or []
        if legs:
            leg = legs[0]
            flights.append({
                "airline": leg.get("airline"),
                "duration": leg.get("duration"),
                "departure_airport": leg.get("departure_airport"),
                "arrival_airport": leg.get("arrival_airport"),
                "departure_time": leg.get("departure_time"),
                "arrival_time": leg.get("arrival_time"),
                "price": price,
            })
    return flights or data

def search_places(city: str):
    params = {"engine": "google_maps", "q": f"Atracción turística en {city}", "api_key": SERP_API_KEY}
    data = _get(params)
    places = []
    for p in (data.get("local_results") or [])[:6]:
        links = p.get("links")
        first_link = None
        if isinstance(links, list) and links:
            first = links[0]
            if isinstance(first, dict):
                first_link = first.get("link")
        places.append({
            "name": p.get("title"),
            "rating": p.get("rating"),
            "address": p.get("address"),
            "link": first_link,
        })
    return places or data

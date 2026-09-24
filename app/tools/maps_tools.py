# app/tools/maps_tools.py
"""Google Maps Geocoding and Places (New) API function tools."""

import json
import os
import urllib.parse
import urllib.request
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from local .env file
load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")


def _get_api_key() -> str:
    """Retrieve Google Maps API key from environment variable."""
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_MAPS_API_KEY environment variable is missing in .env")
    return api_key


def geocode_address(address: str) -> str:
    """Turn a street address or city name into geographical coordinates (latitude and longitude).

    Args:
        address: Full street address or location name (e.g. '1600 Amphitheatre Pkwy, Mountain View, CA').

    Returns:
        Formatted string containing formatted address, latitude, and longitude.
    """
    try:
        api_key = _get_api_key()
        encoded_address = urllib.parse.quote(address.strip())
        url = f"https://maps.googleapis.com/maps/api/geocode/json?address={encoded_address}&key={api_key}"

        req = urllib.request.Request(url, headers={"User-Agent": "GroceryAssistant/1.0"})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())

        if data.get("status") != "OK" or not data.get("results"):
            return f"Could not geocode address '{address}': {data.get('status', 'No results')}"

        first_result = data["results"][0]
        formatted_address = first_result.get("formatted_address")
        location = first_result.get("geometry", {}).get("location", {})
        lat = location.get("lat")
        lng = location.get("lng")

        return (
            f"📍 Geocoded Result:\n"
            f"Address: {formatted_address}\n"
            f"Latitude: {lat}\n"
            f"Longitude: {lng}"
        )
    except Exception as e:
        return f"Geocoding error: {str(e)}"


def find_nearby_places(
    latitude: float,
    longitude: float,
    place_type: str = "grocery_store",
    radius_meters: float = 5000.0,
) -> str:
    """Find nearby places (such as grocery stores, supermarkets, or bakeries) around a location using Places API (New).

    Args:
        latitude: Center point latitude (e.g. 37.422).
        longitude: Center point longitude (e.g. -122.084).
        place_type: Place type tag (e.g. 'grocery_store', 'supermarket', 'bakery', 'restaurant').
        radius_meters: Search radius in meters (default: 5000 meters / ~3 miles).

    Returns:
        Formatted summary of nearby places including name, address, and coordinates.
    """
    try:
        api_key = _get_api_key()
        url = "https://places.googleapis.com/v1/places:searchNearby"

        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": api_key,
            "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.location",
            "User-Agent": "GroceryAssistant/1.0",
        }

        # Map common clean type names if needed
        type_clean = place_type.lower().strip()
        included_types = [type_clean]
        if type_clean in ("grocery", "grocery store", "grocery_store"):
            included_types = ["grocery_store", "supermarket"]

        payload = {
            "includedTypes": included_types,
            "maxResultCount": 5,
            "locationRestriction": {
                "circle": {
                    "center": {
                        "latitude": float(latitude),
                        "longitude": float(longitude),
                    },
                    "radius": float(radius_meters),
                }
            },
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())

        places = data.get("places", [])
        if not places:
            return f"No nearby '{place_type}' places found within {radius_meters}m of ({latitude}, {longitude})."

        results = [f"🏬 Nearby {place_type.title()} Places:"]
        for p in places:
            name = p.get("displayName", {}).get("text", "Unknown Place")
            addr = p.get("formattedAddress", "No address")
            loc = p.get("location", {})
            p_lat = loc.get("latitude")
            p_lng = loc.get("longitude")

            results.append(
                f"- **{name}**\n"
                f"  Address: {addr}\n"
                f"  Location: ({p_lat}, {p_lng})"
            )

        return "\n".join(results)
    except Exception as e:
        return f"Places API search error: {str(e)}"

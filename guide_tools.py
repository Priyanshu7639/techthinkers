import requests

OPENTRIPMAP_API_KEY = "5ae2e3f221c38a28845f05b6cab57648414f564a6bfcabca8e21b249"

def get_city_coords(city_name):
    url = f"https://api.opentripmap.com/0.1/en/places/geoname?name={city_name}&apikey={OPENTRIPMAP_API_KEY}"
    res = requests.get(url)
    data = res.json()
    return data.get("lat"), data.get("lon")

def get_places_nearby(lat, lng, radius=5000, kinds="interesting_places"):
    url = (
        f"https://api.opentripmap.com/0.1/en/places/radius?"
        f"radius={radius}&lon={lng}&lat={lat}&kinds={kinds}&format=json&apikey={OPENTRIPMAP_API_KEY}"
    )
    response = requests.get(url)
    places_data = response.json()

    places = []
    for p in places_data[:10]:  # limit to top 10 for simplicity
        place_name = p.get("name")
        xid = p.get("xid")

        # fetch detailed info for better description
        if xid:
            detail_url = f"https://api.opentripmap.com/0.1/en/places/xid/{xid}?apikey={OPENTRIPMAP_API_KEY}"
            detail_res = requests.get(detail_url).json()
            place_info = {
                "name": place_name,
                "address": detail_res.get("address", {}).get("road", "Unknown"),
                "desc": detail_res.get("wikipedia_extracts", {}).get("text", "No description available."),
                "rating": round(detail_res.get("rate", 1), 1)
            }
            places.append(place_info)

    return places

from agents.guide_agent import run_guide_agent

def guide_tool(latitude=None, longitude=None, city=None):
    return run_guide_agent(latitude, longitude, city)

import requests
import os

ORS_API_KEY = "5b3ce3597851110001cf6248f87887971dee4d96b362f5dd59e9c6ca"
CLIMATIQ_API_KEY = "58HW6K5PRD3S90MH1ZPDEHZ3QM"

from agents.decision_agent import run_decision_agent

def decision_tool(source, destination, priority):
    return run_decision_agent(source, destination, priority)

def get_route_info(source_coords, dest_coords):
    modes = ["cycling-regular", "driving-car", "foot-walking", "driving-hgv"]
    mode_names = {
        "cycling-regular": "Bike",
        "driving-car": "Cab",
        "foot-walking": "Walk",
        "driving-hgv": "Bus"
    }

    results = []

    for mode in modes:
        url = f"https://api.openrouteservice.org/v2/directions/{mode}"
        headers = {
            "Authorization": ORS_API_KEY
        }
        params = {
            "start": f"{source_coords[1]},{source_coords[0]}",
            "end": f"{dest_coords[1]},{dest_coords[0]}"
        }

        try:
            response = requests.get(url, headers=headers, params=params)
            data = response.json()
            distance_km = data['features'][0]['properties']['segments'][0]['distance'] / 1000
            duration_min = data['features'][0]['properties']['segments'][0]['duration'] / 60

            co2 = get_co2_estimate(distance_km, mode)

            # Basic cost estimate (can be improved later)
            cost = {
                "Bike": 10,
                "Walk": 0,
                "Cab": round(distance_km * 15),
                "Bus": 15
            }.get(mode_names[mode], 0)

            results.append({
                "mode": mode_names[mode],
                "distance_km": round(distance_km, 2),
                "time_min": round(duration_min, 2),
                "cost_inr": cost,
                "co2_g": round(co2, 2)
            })

        except Exception as e:
            results.append({
                "mode": mode_names[mode],
                "error": str(e)
            })

    return {"modes": results}


def get_co2_estimate(distance_km, mode):
    # Map to Climatiq transport activity IDs
    activity_ids = {
        "cycling-regular": "passenger_vehicle-vehicle_type_bicycle-fuel_source_na-engine_size_na",
        "foot-walking": "passenger_vehicle-vehicle_type_na-fuel_source_na-engine_size_na",  # minimal footprint
        "driving-car": "passenger_vehicle-vehicle_type_medium-fuel_source_petrol-engine_size_na",
        "driving-hgv": "bus-vehicle_type_na-fuel_source_diesel-engine_size_na"
    }

    body = {
        "emission_factor": {
            "activity_id": activity_ids.get(mode, "passenger_vehicle-vehicle_type_medium-fuel_source_petrol-engine_size_na")
        },
        "parameters": {
            "distance": distance_km,
            "distance_unit": "km"
        }
    }

    headers = {
        "Authorization": f"Bearer {CLIMATIQ_API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post("https://beta3.api.climatiq.io/estimate", json=body, headers=headers)
    data = response.json()
    return data.get("co2e", 0) * 1000  # kg to grams

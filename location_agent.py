import requests
from utlis.tools import get_nearby_transit_stations

HF_API_TOKEN = "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"  # Replace with your Hugging Face token
HF_MODEL = "HuggingFaceH4/zephyr-7b-beta"

def query_huggingface_model(prompt):
    headers = {
        "Authorization": f"Bearer {HF_API_TOKEN}"
    }
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 300,
            "do_sample": True,
            "temperature": 0.7
        }
    }

    response = requests.post(
        f"https://api-inference.huggingface.co/models/{HF_MODEL}",
        headers=headers,
        json=payload
    )

    try:
        response.raise_for_status()
        result = response.json()
        if isinstance(result, list) and "generated_text" in result[0]:
            return result[0]["generated_text"]
        elif isinstance(result, dict) and "error" in result:
            return f"Model error: {result['error']}"
        else:
            return "⚠️ Received unexpected response format."
    except requests.exceptions.HTTPError as e:
        return f"HTTP error: {e.response.status_code} - {e.response.text}"
    except Exception as e:
        return f"Unhandled error: {str(e)}"

def run_location_agent(lat, lng):
    stations = get_nearby_transit_stations(lat, lng)

    formatted_stations = "\n".join([
        f"- {s['name']} ({s['type']}, {s['distance_km']} km)" for s in stations
    ])

    prompt = f"""
You are a smart AI travel assistant helping users plan eco-friendly city travel.

The user is currently at:
Latitude: {lat}
Longitude: {lng}

Here are nearby public transport options:
{formatted_stations}

Please suggest 2-3 best eco-friendly options within 2 km and explain why they are good choices.
"""

    return query_huggingface_model(prompt)

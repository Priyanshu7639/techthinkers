import requests
from utlis.guide_tools import get_city_coords, get_places_nearby

HF_API_TOKEN = "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"
HF_MODEL = "HuggingFaceH4/zephyr-7b-beta"

def query_guide_model(prompt):
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
    payload = {
        "inputs": prompt,
        "parameters": {"max_new_tokens": 400, "do_sample": False, "temperature": 0.6}
    }
    response = requests.post(
        f"https://api-inference.huggingface.co/models/{HF_MODEL}",
        headers=headers,
        json=payload
    )
    try:
        result = response.json()
        return result[0]["generated_text"]
    except Exception as e:
        return f"Error: {str(e)}"

def run_guide_agent(lat=None, lng=None, city=None):
    if city:
        lat, lng = get_city_coords(city)
        if not lat or not lng:
            return f"Sorry, I couldn't locate the city: {city}."

    places = get_places_nearby(lat, lng)

    if not places:
        return f"Sorry, I couldn't find tourist attractions near {city or 'your location'}."

    formatted = "\n".join([
        f"- {p['name']} (⭐ {p['rating']}) - {p['desc'][:80]}..." for p in places
    ])

    prompt = f"""
You are a friendly travel guide.

The user is visiting {city or 'a new location'}.

Here are tourist spots in the area:
{formatted}

Recommend these places with 2-3 must-visits and suggest an eco-friendly travel tip.
"""

    return query_guide_model(prompt)

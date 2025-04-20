# agents/decision_agent.py

import requests
from utlis.decision_tools import get_route_info

HF_API_TOKEN = "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"
HF_MODEL = "HuggingFaceH4/zephyr-7b-beta"

def query_model(prompt):
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
        result = response.json()
        return result[0]["generated_text"]
    except Exception as e:
        return f"Error: {str(e)}"

def run_decision_agent(source, destination, priority="eco-friendly"):
    routes = get_route_info(source, destination)
    prompt = f"""
You are an expert eco-travel advisor. The user wants to go from {source} to {destination}.
Here are travel options with estimated values:

{routes['modes']}

User priority: {priority}

Your job is to analyze these options and recommend the best travel mode based on:
- Lowest CO₂ (for eco)
- Lowest cost (for economical)
- Shortest time (for fastest)

Respond with a clear recommendation and short reason.
"""
    return query_model(prompt)

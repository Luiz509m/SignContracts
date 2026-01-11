import os
import json
import requests

API_KEY = os.getenv("LLM_API_KEY")
API_URL = "https://api.openai.com/v1/chat/completions"


def parse_llm_json(raw_text: str) -> dict:
    """
    Entfernt ```json``` Markdown und wandelt den Text in ein Python-Dictionary um.
    """
    cleaned = raw_text.strip()

    if cleaned.startswith("```"):
        cleaned = cleaned.replace("```json", "")
        cleaned = cleaned.replace("```", "")
        cleaned = cleaned.strip()

    return json.loads(cleaned)


def analyze_contract(text: str) -> dict:
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    system_prompt = (
        "Du bist ein Assistent für Geschäftsführer kleiner Unternehmen. "
        "Du analysierst IT- und Service-Wartungsverträge. "
        "Du gibst KEINE Rechtsberatung. "
        "Wenn Informationen fehlen oder unklar sind, verwende null oder false."
    )

    user_prompt = f"""
Analysiere den folgenden Vertragstext und extrahiere die Informationen.
Antworte ausschließlich im folgenden JSON-Format.

JSON-Format:
{{
  "leistungsumfang": string | null,
  "laufzeit_monate": number | null,
  "automatische_verlaengerung": boolean,
  "monatliche_kosten": number | null,
  "zusatzkosten_nach_aufwand": boolean,
  "sla_vorhanden": boolean,
  "haftung_datenverlust": string | null,
  "preisanpassung_vorhanden": boolean
}}

Vertragstext:
{text}
"""

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0
    }

    response = requests.post(
    API_URL,
    headers=headers,
    json=payload,
    timeout=130  # Sekunden
)
    response.raise_for_status()


    content = response.json()["choices"][0]["message"]["content"]

    # 🔑 ENTSCHEIDENDER SCHRITT
    parsed_json = parse_llm_json(content)

    return parsed_json

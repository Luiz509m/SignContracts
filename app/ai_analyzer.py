import os
import requests
import json

API_KEY = os.getenv("LLM_API_KEY")
API_URL = "https://api.openai.com/v1/chat/completions"

def analyze_contract(text: str) -> dict:
    """
    Analysiert einen Vertragstext mit OpenAI und gibt strukturierte Daten zurück
    """
    
    if not API_KEY:
        raise ValueError("LLM_API_KEY nicht gesetzt")
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    system_prompt = (
        "Du bist ein Assistent für Geschäftsführer kleiner Handwerksbetriebe. "
        "Du analysierst IT- und Service-Wartungsverträge. "
        "Du gibst KEINE Rechtsberatung. "
        "Wenn Informationen fehlen oder unklar sind, verwende null oder false. "
        "Antworte AUSSCHLIESSLICH mit validem JSON, ohne Markdown-Formatierung."
    )
    
    user_prompt = f"""
Analysiere den folgenden Vertragstext und extrahiere die Informationen.
Antworte ausschließlich im folgenden JSON-Format (ohne ```json oder andere Formatierung):

{{
  "leistungsumfang": "string oder null",
  "laufzeit_monate": number oder null,
  "automatische_verlaengerung": boolean,
  "monatliche_kosten": number oder null,
  "zusatzkosten_nach_aufwand": boolean,
  "sla_vorhanden": boolean,
  "haftung_datenverlust": "string oder null",
  "preisanpassung_vorhanden": boolean
}}

Vertragstext:
{text[:6000]}
"""
    
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0,
        "max_tokens": 500
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        
        content = response.json()["choices"][0]["message"]["content"]
        
        # Entferne mögliche Markdown-Formatierung
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
        
        # Parse JSON
        try:
            data = json.loads(content)
            return data
        except json.JSONDecodeError:
            # Fallback wenn JSON kaputt ist
            return {
                "leistungsumfang": "Analyse fehlgeschlagen - bitte versuchen Sie es erneut",
                "laufzeit_monate": None,
                "automatische_verlaengerung": False,
                "monatliche_kosten": None,
                "zusatzkosten_nach_aufwand": False,
                "sla_vorhanden": False,
                "haftung_datenverlust": None,
                "preisanpassung_vorhanden": False
            }
    
    except requests.exceptions.Timeout:
        raise Exception("OpenAI API Timeout - bitte versuchen Sie es erneut")
    except requests.exceptions.RequestException as e:
        raise Exception(f"OpenAI API Fehler: {str(e)}")
    except Exception as e:
        raise Exception(f"Analyse fehlgeschlagen: {str(e)}")

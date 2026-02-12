import os
import requests
import json

API_KEY = os.getenv("LLM_API_KEY")
API_URL = "https://api.anthropic.com/v1/messages"

def analyze_contract(text: str) -> dict:
    """
    Analysiert einen Vertragstext mit Claude (Anthropic) und gibt strukturierte Daten zurück
    """
    
    # DEBUGGING
    print(f"=== DEBUG START ===")
    print(f"API_KEY gesetzt: {bool(API_KEY)}")
    if API_KEY:
        print(f"API_KEY beginnt mit: {API_KEY[:15]}...")
        print(f"API_KEY Länge: {len(API_KEY)}")
    print(f"Text Länge: {len(text)}")
    print(f"=== DEBUG ENDE ===")
    
    if not API_KEY:
        raise ValueError("LLM_API_KEY nicht gesetzt")
    
    headers = {
        "x-api-key": API_KEY,
        "anthropic-version": "2023-06-01",
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
        "model": "claude-3-5-haiku-20241022",  # Günstigstes Modell
        "max_tokens": 1024,
        "system": system_prompt,
        "messages": [
            {"role": "user", "content": user_prompt}
        ]
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=120)
        response.raise_for_status()
        
        content = response.json()["content"][0]["text"]
        
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
        raise Exception("API Timeout - bitte versuchen Sie es erneut")
    except requests.exceptions.RequestException as e:
        raise Exception(f"API Fehler: {str(e)}")
    except Exception as e:
        raise Exception(f"Analyse fehlgeschlagen: {str(e)}")

import os
import requests
import json

API_KEY = os.getenv("LLM_API_KEY")
API_URL = "https://api.anthropic.com/v1/messages"

def analyze_contract(text: str) -> dict:
    """
    Analysiert JEDEN Vertragstyp mit Claude in 2 Schritten:
    1. Vertragstyp erkennen
    2. Spezifische Analyse durchführen
    """
    
    print(f"=== ANALYSE START ===")
    print(f"Text Länge: {len(text)} Zeichen")
    
    if not API_KEY:
        raise ValueError("LLM_API_KEY nicht gesetzt")
    
    # SCHRITT 1: Vertragstyp erkennen
    contract_type = detect_contract_type(text)
    print(f"📋 Erkannter Vertragstyp: {contract_type}")
    
    # SCHRITT 2: Vertragsanalyse
    analysis = analyze_by_type(text, contract_type)
    print(f"✅ Analyse abgeschlossen")
    
    return analysis


def detect_contract_type(text: str) -> str:
    """
    Erkennt den Vertragstyp automatisch
    """
    
    headers = {
        "x-api-key": API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    
    prompt = f"""
Analysiere diesen Vertragstext und bestimme den Vertragstyp.

Antworte NUR mit EINEM dieser Typen (nichts anderes):
- IT_SERVICE (Software, Cloud, Hosting, IT-Support, Wartung)
- HANDWERK (Renovation, Bau, Handwerksleistungen)
- MIETVERTRAG (Wohnung, Büro, Lager)
- ARBEITSVERTRAG (Anstellung, Arbeitsverhältnis)
- KAUFVERTRAG (Warenkauf, Lieferung)
- DIENSTLEISTUNG (Beratung, Freelance, sonstige Services)
- SONSTIGES (wenn unklar)

Vertragstext:
{text[:3000]}

Antwort (nur der Typ):
"""
    
    payload = {
        "model": "claude-3-5-sonnet-20241022",
        "max_tokens": 50,
        "messages": [{"role": "user", "content": prompt}]
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        contract_type = response.json()["content"][0]["text"].strip()
        
        # Validierung
        valid_types = ["IT_SERVICE", "HANDWERK", "MIETVERTRAG", "ARBEITSVERTRAG", 
                      "KAUFVERTRAG", "DIENSTLEISTUNG", "SONSTIGES"]
        
        if contract_type not in valid_types:
            return "SONSTIGES"
        
        return contract_type
        
    except Exception as e:
        print(f"⚠️ Typerkennung fehlgeschlagen: {e}")
        return "SONSTIGES"


def analyze_by_type(text: str, contract_type: str) -> dict:
    """
    Analysiert den Vertrag basierend auf seinem Typ
    """
    
    headers = {
        "x-api-key": API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    
    # Typ-spezifische Prompts
    type_prompts = {
        "IT_SERVICE": get_it_service_prompt(),
        "HANDWERK": get_handwerk_prompt(),
        "MIETVERTRAG": get_miet_prompt(),
        "ARBEITSVERTRAG": get_arbeits_prompt(),
        "KAUFVERTRAG": get_kauf_prompt(),
        "DIENSTLEISTUNG": get_dienstleistung_prompt(),
        "SONSTIGES": get_general_prompt()
    }
    
    analysis_prompt = type_prompts.get(contract_type, get_general_prompt())
    
    user_prompt = f"""
{analysis_prompt}

Vertragstext:
{text[:6000]}
"""
    
    payload = {
        "model": "claude-3-5-sonnet-20241022",
        "max_tokens": 2000,
        "messages": [{"role": "user", "content": user_prompt}]
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=120)
        response.raise_for_status()
        
        content = response.json()["content"][0]["text"]
        
        # JSON extrahieren
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
        
        data = json.loads(content)
        
        # Vertragstyp hinzufügen
        data["vertragstyp"] = contract_type
        
        return data
        
    except json.JSONDecodeError as e:
        print(f"⚠️ JSON Parse Error: {e}")
        return get_fallback_response(contract_type)
    except Exception as e:
        print(f"❌ Analyse Fehler: {e}")
        raise Exception(f"Analyse fehlgeschlagen: {str(e)}")


# ==================== PROMPTS FÜR JEDEN VERTRAGSTYP ====================

def get_it_service_prompt():
    return """
Analysiere diesen IT-Service/Wartungsvertrag und extrahiere folgende Informationen.
Antworte NUR mit validem JSON (ohne Markdown):

{
  "leistungsumfang": "Beschreibung der Leistungen oder null",
  "laufzeit_monate": number oder null,
  "automatische_verlaengerung": boolean,
  "monatliche_kosten": number oder null,
  "kuendigungsfrist_monate": number oder null,
  "sla_vorhanden": boolean,
  "sla_details": "Details oder null",
  "haftung_datenverlust": "Beschreibung oder null",
  "preisanpassung_regelung": "Beschreibung oder null",
  "datenschutz_erwähnt": boolean,
  "top_risiken": ["Risiko 1", "Risiko 2", "Risiko 3"]
}
"""

def get_handwerk_prompt():
    return """
Analysiere diesen Handwerks-/Bauvertrag und extrahiere folgende Informationen.
Antworte NUR mit validem JSON (ohne Markdown):

{
  "leistungsumfang": "Beschreibung oder null",
  "gesamtpreis": number oder null,
  "anzahlung_prozent": number oder null,
  "anzahlung_betrag": number oder null,
  "beginn_datum": "Datum oder null",
  "ende_datum": "Datum oder null",
  "vertragsstrafe_bei_verzug": boolean,
  "vertragsstrafe_details": "Details oder null",
  "gewaehrleistung_monate": number oder null,
  "haftung_beschraenkt": boolean,
  "haftung_details": "Details oder null",
  "maengel_meldefrist_tage": number oder null,
  "top_risiken": ["Risiko 1", "Risiko 2", "Risiko 3"]
}
"""

def get_miet_prompt():
    return """
Analysiere diesen Mietvertrag und extrahiere folgende Informationen.
Antworte NUR mit validem JSON (ohne Markdown):

{
  "mietobjekt": "Beschreibung oder null",
  "miete_monatlich": number oder null,
  "nebenkosten_monatlich": number oder null,
  "kaution_betrag": number oder null,
  "mietbeginn": "Datum oder null",
  "befristet": boolean,
  "mietende": "Datum oder null",
  "kuendigungsfrist_monate": number oder null,
  "kleinreparaturen_mieter": boolean,
  "kleinreparaturen_grenze": number oder null,
  "indexierung": boolean,
  "top_risiken": ["Risiko 1", "Risiko 2", "Risiko 3"]
}
"""

def get_arbeits_prompt():
    return """
Analysiere diesen Arbeitsvertrag und extrahiere folgende Informationen.
Antworte NUR mit validem JSON (ohne Markdown):

{
  "position": "Bezeichnung oder null",
  "gehalt_jaehrlich": number oder null,
  "gehalt_monatlich": number oder null,
  "arbeitsbeginn": "Datum oder null",
  "befristet": boolean,
  "vertragsende": "Datum oder null",
  "probezeit_monate": number oder null,
  "wochenarbeitszeit": number oder null,
  "urlaubstage": number oder null,
  "kuendigungsfrist_monate": number oder null,
  "konkurrenzverbot": boolean,
  "top_risiken": ["Risiko 1", "Risiko 2", "Risiko 3"]
}
"""

def get_kauf_prompt():
    return """
Analysiere diesen Kaufvertrag und extrahiere folgende Informationen.
Antworte NUR mit validem JSON (ohne Markdown):

{
  "kaufgegenstand": "Beschreibung oder null",
  "kaufpreis": number oder null,
  "lieferdatum": "Datum oder null",
  "zahlungsbedingungen": "Beschreibung oder null",
  "gewaehrleistung_monate": number oder null,
  "ruecktrittsrecht": boolean,
  "ruecktrittsrecht_tage": number oder null,
  "haftung_beschraenkt": boolean,
  "top_risiken": ["Risiko 1", "Risiko 2", "Risiko 3"]
}
"""

def get_dienstleistung_prompt():
    return """
Analysiere diesen Dienstleistungsvertrag und extrahiere folgende Informationen.
Antworte NUR mit validem JSON (ohne Markdown):

{
  "leistungsumfang": "Beschreibung oder null",
  "verguetung": number oder null,
  "verguetung_typ": "Stundensatz/Pauschal/Monatlich oder null",
  "laufzeit_monate": number oder null,
  "kuendigungsfrist_monate": number oder null,
  "haftung_beschraenkt": boolean,
  "vertraulichkeit_vereinbart": boolean,
  "top_risiken": ["Risiko 1", "Risiko 2", "Risiko 3"]
}
"""

def get_general_prompt():
    return """
Analysiere diesen Vertrag und extrahiere die wichtigsten Informationen.
Antworte NUR mit validem JSON (ohne Markdown):

{
  "vertragsgegenstand": "Beschreibung oder null",
  "parteien": "Beschreibung oder null",
  "laufzeit": "Beschreibung oder null",
  "kosten": "Beschreibung oder null",
  "kuendigung": "Beschreibung oder null",
  "haftung": "Beschreibung oder null",
  "top_risiken": ["Risiko 1", "Risiko 2", "Risiko 3"]
}
"""


def get_fallback_response(contract_type: str) -> dict:
    """Fallback wenn JSON-Parsing fehlschlägt"""
    return {
        "vertragstyp": contract_type,
        "fehler": "Analyse teilweise fehlgeschlagen",
        "top_risiken": [
            "Automatische Analyse fehlgeschlagen - bitte manuell prüfen",
            "Vertrag sollte von Fachperson geprüft werden"
        ]
    }

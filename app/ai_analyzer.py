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
        
        if contract_type not in valid_ty

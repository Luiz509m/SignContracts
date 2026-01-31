def analyze_contract(text: str):
    return {
        "ampel": "gelb",
        "top_risiken": [
            {"beschreibung": "Keine SLA definiert"}
        ],
        "empfehlungen": [
            "SLA vertraglich festhalten"
        ],
        "mail": {
            "text": "Bitte SLA nachreichen."
        }
    }

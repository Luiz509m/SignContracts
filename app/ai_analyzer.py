def analyze_contract(text: str):
    text_lower = text.lower()

    checks = {}

    # =====================
    # Laufzeit
    # =====================
    if "36 monate" in text_lower or "drei jahre" in text_lower:
        checks["laufzeit"] = {
            "bewertung": "kritisch",
            "text": "Laufzeit von 36 Monaten ist für IT- oder Wartungsverträge ungewöhnlich lang."
        }
    else:
        checks["laufzeit"] = {
            "bewertung": "ok",
            "text": "Keine ungewöhnlich lange Laufzeit erkannt."
        }

    # =====================
    # Kündigung
    # =====================
    if "kündigungsfrist" in text_lower:
        checks["kuendigung"] = {
            "bewertung": "ok",
            "text": "Kündigungsfrist ist im Vertrag geregelt."
        }
    else:
        checks["kuendigung"] = {
            "bewertung": "kritisch",
            "text": "Keine klare Kündigungsfrist gefunden."
        }

    # =====================
    # SLA
    # =====================
    if "sla" in text_lower or "service level" in text_lower:
        checks["sla"] = {
            "bewertung": "ok",
            "text": "Service Level Agreements sind erwähnt."
        }
    else:
        checks["sla"] = {
            "bewertung": "kritisch",
            "text": "Keine Service Level Agreements definiert."
        }

    # =====================
    # Ampel bestimmen
    # =====================
    kritisch = sum(1 for c in checks.values() if c["bewertung"] == "kritisch")

    if kritisch >= 2:
        ampel = "rot"
    elif kritisch == 1:
        ampel = "gelb"
    else:
        ampel = "grün"

    # =====================
    # Empfehlungen
    # =====================
    empfehlungen = []
    if checks["laufzeit"]["bewertung"] == "kritisch":
        empfehlungen.append("Laufzeit auf maximal 12 Monate begrenzen.")
    if checks["sla"]["bewertung"] == "kritisch":
        empfehlungen.append("SLA mit Reaktions- und Lösungszeiten ergänzen.")
    if checks["kuendigung"]["bewertung"] == "kritisch":
        empfehlungen.append("Klare Kündigungsfrist im Vertrag festlegen.")

    return {
        "ampel": ampel,
        "zusammenfassung": "Automatisierte Erstprüfung des Vertrags mit Fokus auf typische Risiken.",
        "checks": checks,
        "empfehlungen": empfehlungen,
        "mail": {
            "text": "Bitte prüfen Sie die angesprochenen Punkte und senden Sie uns eine überarbeitete Vertragsversion."
        },
        "hinweis": "Keine Rechtsberatung"
    }

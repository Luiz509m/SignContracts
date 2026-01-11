def detect_risks(analysis: dict) -> list:
    risks = []

    # Laufzeit & Kündigung
    if analysis.get("laufzeit_monate") and analysis["laufzeit_monate"] > 12:
        risks.append({
            "kategorie": "Laufzeit & Kündigung",
            "beschreibung": "Laufzeit über 12 Monate führt zu hoher langfristiger Bindung."
        })

    if analysis.get("automatische_verlaengerung"):
        risks.append({
            "kategorie": "Laufzeit & Kündigung",
            "beschreibung": "Automatische Vertragsverlängerung kann ungewollte Bindung verursachen."
        })

    # Kosten & Zusatzkosten
    if analysis.get("zusatzkosten_nach_aufwand"):
        risks.append({
            "kategorie": "Kosten & Zusatzleistungen",
            "beschreibung": "Zusatzleistungen werden nach Aufwand abgerechnet, Kosten sind nicht klar planbar."
        })

    # SLA
    if analysis.get("sla_vorhanden") is False:
        risks.append({
            "kategorie": "SLA / Reaktionszeiten",
            "beschreibung": "Keine garantierten Reaktionszeiten oder Eskalationsstufen definiert."
        })

    return risks
def calculate_traffic_light(risks: list) -> str:
    if len(risks) >= 3:
        return "rot"
    if len(risks) >= 1:
        return "gelb"
    return "gruen"
def get_top_risks(risks: list, limit: int = 3) -> list:
    return risks[:limit]
def generate_recommendations(risks: list) -> list:
    recommendations = []

    for risk in risks:
        if risk["kategorie"] == "Laufzeit & Kündigung":
            recommendations.append(
                "Laufzeit auf maximal 12 Monate reduzieren und automatische Verlängerung optional gestalten."
            )

        if risk["kategorie"] == "Kosten & Zusatzleistungen":
            recommendations.append(
                "Zusatzleistungen klar bepreisen oder eine Kostenobergrenze vereinbaren."
            )

        if risk["kategorie"] == "SLA / Reaktionszeiten":
            recommendations.append(
                "Reaktionszeiten und Eskalationsstufen schriftlich im Vertrag festlegen."
            )

    return list(dict.fromkeys(recommendations))  # Duplikate entfernen
def generate_mail(recommendations: list) -> dict:
    bullet_points = "\n".join([f"- {r}" for r in recommendations])

    text = f"""Guten Tag,

vielen Dank für Ihr Angebot. Bevor wir den Vertrag final unterzeichnen, bitten wir um Klärung folgender Punkte:

{bullet_points}

Vielen Dank für Ihre Rückmeldung.

Freundliche Grüße
"""

    return {
        "betreff": "Rückfragen zu IT-Wartungsvertrag",
        "text": text
    }
def build_decision_output(analysis: dict) -> dict:
    risks = detect_risks(analysis)
    ampel = calculate_traffic_light(risks)
    top_risks = get_top_risks(risks)
    recommendations = generate_recommendations(top_risks)
    mail = generate_mail(recommendations)

    return {
        "ampel": ampel,
        "top_risiken": top_risks,
        "empfehlungen": recommendations,
        "mail": mail,
        "hinweis": "Diese Bewertung ersetzt keine Rechtsberatung."
    }

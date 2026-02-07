def build_decision_output(analysis: dict) -> dict:
    """
    Wandelt die KI-Analyse in ein strukturiertes Format um
    mit Ampel-Bewertung, Risiken und Empfehlungen
    """
    
    # Ampel-Logik
    ampel = calculate_ampel(analysis)
    
    # Risiken identifizieren
    risiken = identify_risks(analysis)
    
    # Empfehlungen generieren
    empfehlungen = generate_recommendations(analysis)
    
    # E-Mail-Vorlage
    mail = generate_mail_template(analysis, risiken)
    
    return {
        "ampel": ampel,
        "top_risiken": risiken,
        "empfehlungen": empfehlungen,
        "mail": {"text": mail},
        "raw_data": analysis
    }


def calculate_ampel(data: dict) -> str:
    """Berechnet Ampel-Status basierend auf Vertragsdaten"""
    risk_score = 0
    
    # Automatische Verlängerung = Risiko
    if data.get("automatische_verlaengerung", False):
        risk_score += 2
    
    # Lange Laufzeit = Risiko
    laufzeit = data.get("laufzeit_monate", 0) or 0
    if laufzeit > 24:
        risk_score += 2
    elif laufzeit > 12:
        risk_score += 1
    
    # Fehlende SLAs = Risiko
    if not data.get("sla_vorhanden", False):
        risk_score += 1
    
    # Unklare Haftung = Risiko
    if not data.get("haftung_datenverlust"):
        risk_score += 2
    
    # Preisanpassungsklausel = Risiko
    if data.get("preisanpassung_vorhanden", False):
        risk_score += 1
    
    # Ampel-Bewertung
    if risk_score >= 5:
        return "rot"
    elif risk_score >= 2:
        return "gelb"
    else:
        return "gruen"


def identify_risks(data: dict) -> list:
    """Identifiziert konkrete Risiken im Vertrag"""
    risiken = []
    
    if data.get("automatische_verlaengerung", False):
        risiken.append({
            "beschreibung": "Automatische Vertragsverlängerung ohne aktive Zustimmung"
        })
    
    laufzeit = data.get("laufzeit_monate", 0) or 0
    if laufzeit > 24:
        risiken.append({
            "beschreibung": f"Lange Vertragslaufzeit von {laufzeit} Monaten - eingeschränkte Flexibilität"
        })
    
    if not data.get("sla_vorhanden", False):
        risiken.append({
            "beschreibung": "Keine Service Level Agreements (SLA) definiert - unklare Leistungsgarantien"
        })
    
    if not data.get("haftung_datenverlust"):
        risiken.append({
            "beschreibung": "Haftung bei Datenverlust nicht klar geregelt"
        })
    
    if data.get("preisanpassung_vorhanden", False):
        risiken.append({
            "beschreibung": "Anbieter kann Preise einseitig anpassen"
        })
    
    if data.get("zusatzkosten_nach_aufwand", False):
        risiken.append({
            "beschreibung": "Zusatzkosten nach Aufwand - Budget schwer planbar"
        })
    
    # Falls keine Risiken gefunden
    if not risiken:
        risiken.append({
            "beschreibung": "Keine kritischen Risiken identifiziert"
        })
    
    return risiken


def generate_recommendations(data: dict) -> list:
    """Generiert konkrete Handlungsempfehlungen"""
    empfehlungen = []
    
    if data.get("automatische_verlaengerung", False):
        empfehlungen.append("Nachverhandeln: Klausel zur automatischen Verlängerung ändern oder Kündigungsfrist verkürzen")
    
    if not data.get("sla_vorhanden", False):
        empfehlungen.append("SLA-Vereinbarung einfordern mit konkreten Verfügbarkeitsgarantien (z.B. 99,5%)")
    
    if not data.get("haftung_datenverlust"):
        empfehlungen.append("Haftungsregelungen präzisieren, besonders für Datenverlust und Ausfallzeiten")
    
    if data.get("preisanpassung_vorhanden", False):
        empfehlungen.append("Preisanpassungsklausel begrenzen (z.B. max. Inflationsrate, Zustimmungsvorbehalt)")
    
    laufzeit = data.get("laufzeit_monate", 0) or 0
    if laufzeit > 24:
        empfehlungen.append("Kürzere Vertragslaufzeit vereinbaren oder Sonderkündigungsrecht bei Änderungen")
    
    # Falls keine spezifischen Empfehlungen
    if not empfehlungen:
        empfehlungen.append("Vertrag scheint ausgeglichen - vor Unterschrift nochmals komplett durchlesen")
    
    return empfehlungen


def generate_mail_template(data: dict, risiken: list) -> str:
    """Generiert E-Mail-Vorlage für Rückfragen"""
    
    leistungsumfang = data.get("leistungsumfang", "die angebotenen Leistungen")
    
    mail = f"""Sehr geehrte Damen und Herren,

vielen Dank für Ihr Vertragsangebot bezüglich {leistungsumfang}.

Nach Prüfung des Vertrags haben wir folgende Rückfragen:

"""
    
    # Füge Risiken als Rückfragen hinzu
    for i, risiko in enumerate(risiken[:3], 1):  # Max. 3 Hauptpunkte
        beschreibung = risiko.get("beschreibung", "")
        mail += f"{i}. {beschreibung}\n   Können wir hier eine Anpassung vereinbaren?\n\n"
    
    mail += """Wir würden uns freuen, diese Punkte gemeinsam zu klären, um eine für beide Seiten faire Vereinbarung zu treffen.

Für ein kurzes Telefonat oder Meeting stehen wir gerne zur Verfügung.

Mit freundlichen Grüßen"""
    
    return mail

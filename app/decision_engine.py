def build_decision_output(analysis: dict) -> dict:
    """
    Erstellt die finale Ausgabe mit Ampel, Risiken und Empfehlungen
    Funktioniert für ALLE Vertragstypen
    """
    
    contract_type = analysis.get("vertragstyp", "SONSTIGES")
    
    # Risiken sammeln
    top_risiken = analysis.get("top_risiken", [])
    
    # Weitere Risiken basierend auf Vertragstyp identifizieren
    additional_risks = identify_risks_by_type(analysis, contract_type)
    
    # Alle Risiken kombinieren
    all_risks = top_risiken + additional_risks
    
    # Duplikate entfernen, max 5 Risiken
    unique_risks = []
    for risk in all_risks:
        if risk not in unique_risks and len(unique_risks) < 5:
            unique_risks.append(risk)
    
    # Ampel-Bewertung
    ampel = calculate_ampel(analysis, contract_type, len(unique_risks))
    
    # Empfehlungen generieren
    empfehlungen = generate_recommendations(analysis, contract_type, ampel)
    
    # E-Mail-Vorlage
    mail_text = generate_email(analysis, contract_type, unique_risks)
    
    return {
        "ampel": ampel,
        "vertragstyp": get_type_label(contract_type),
        "top_risiken": [{"beschreibung": r} for r in unique_risks] if unique_risks else [{"beschreibung": "Keine kritischen Risiken identifiziert"}],
        "empfehlungen": empfehlungen,
        "mail": {"text": mail_text}
    }


def identify_risks_by_type(analysis: dict, contract_type: str) -> list:
    """Identifiziert Risiken basierend auf Vertragstyp"""
    
    risks = []
    
    if contract_type == "IT_SERVICE":
        if not analysis.get("sla_vorhanden"):
            risks.append("Keine Service Level Agreements (SLA) definiert")
        if analysis.get("automatische_verlaengerung"):
            risks.append("Automatische Vertragsverlängerung ohne Kündigungsoption")
        if not analysis.get("haftung_datenverlust"):
            risks.append("Haftung bei Datenverlust nicht geregelt")
    
    elif contract_type == "HANDWERK":
        anzahlung = analysis.get("anzahlung_prozent", 0)
        if anzahlung and anzahlung > 30:
            risks.append(f"Hohe Anzahlung von {anzahlung}% verlangt")
        if not analysis.get("vertragsstrafe_bei_verzug"):
            risks.append("Keine Vertragsstrafe bei Verzug vereinbart")
        if analysis.get("haftung_beschraenkt"):
            risks.append("Haftung des Auftragnehmers stark eingeschränkt")
        gewaehrleistung = analysis.get("gewaehrleistung_monate", 0)
        if gewaehrleistung and gewaehrleistung < 12:
            risks.append(f"Kurze Gewährleistung von nur {gewaehrleistung} Monaten")
    
    elif contract_type == "MIETVERTRAG":
        if analysis.get("indexierung"):
            risks.append("Mietpreisindexierung vereinbart - Miete kann steigen")
        kaution = analysis.get("kaution_betrag", 0)
        miete = analysis.get("miete_monatlich", 0)
        if kaution and miete and kaution > (miete * 3):
            risks.append("Kaution höher als 3 Monatsmieten")
        if analysis.get("kleinreparaturen_mieter"):
            grenze = analysis.get("kleinreparaturen_grenze", 0)
            risks.append(f"Kleinreparaturen zu Lasten Mieter (bis CHF {grenze})")
    
    elif contract_type == "ARBEITSVERTRAG":
        if analysis.get("konkurrenzverbot"):
            risks.append("Konkurrenzverbot nach Vertragsende vereinbart")
        probezeit = analysis.get("probezeit_monate", 0)
        if probezeit and probezeit > 3:
            risks.append(f"Lange Probezeit von {probezeit} Monaten")
        urlaubstage = analysis.get("urlaubstage", 0)
        if urlaubstage and urlaubstage < 20:
            risks.append(f"Wenig Urlaubstage ({urlaubstage} Tage pro Jahr)")
    
    elif contract_type == "KAUFVERTRAG":
        if not analysis.get("ruecktrittsrecht"):
            risks.append("Kein Rücktrittsrecht vereinbart")
        gewaehrleistung = analysis.get("gewaehrleistung_monate", 0)
        if gewaehrleistung and gewaehrleistung < 12:
            risks.append(f"Kurze Gewährleistung von nur {gewaehrleistung} Monaten")
    
    return risks


def calculate_ampel(analysis: dict, contract_type: str, risk_count: int) -> str:
    """Berechnet Ampel-Status"""
    
    # Basis-Bewertung nach Risikoanzahl
    if risk_count >= 4:
        return "rot"
    elif risk_count >= 2:
        return "gelb"
    
    # Typ-spezifische kritische Faktoren
    if contract_type == "HANDWERK":
        anzahlung = analysis.get("anzahlung_prozent", 0)
        if anzahlung and anzahlung > 40:
            return "rot"
        if analysis.get("haftung_beschraenkt") and not analysis.get("vertragsstrafe_bei_verzug"):
            return "gelb"
    
    elif contract_type == "IT_SERVICE":
        if not analysis.get("sla_vorhanden") and analysis.get("automatische_verlaengerung"):
            return "gelb"
    
    elif contract_type == "MIETVERTRAG":
        kaution = analysis.get("kaution_betrag", 0)
        miete = analysis.get("miete_monatlich", 0)
        if kaution and miete and kaution > (miete * 3):
            return "gelb"
    
    return "gruen"


def generate_recommendations(analysis: dict, contract_type: str, ampel: str) -> list:
    """Generiert Handlungsempfehlungen"""
    
    empfehlungen = []
    
    if ampel == "rot":
        empfehlungen.append("⚠️ Vertrag NICHT in aktueller Form unterschreiben")
        empfehlungen.append("Nachverhandlung dringend empfohlen")
    elif ampel == "gelb":
        empfehlungen.append("⚠️ Vertrag kritisch prüfen vor Unterschrift")
        empfehlungen.append("Kritische Punkte klären oder anpassen lassen")
    else:
        empfehlungen.append("✅ Vertrag erscheint weitgehend akzeptabel")
    
    # Typ-spezifische Empfehlungen
    if contract_type == "HANDWERK":
        if not analysis.get("vertragsstrafe_bei_verzug"):
            empfehlungen.append("Vertragsstrafe bei Verzug vereinbaren")
        if analysis.get("haftung_beschraenkt"):
            empfehlungen.append("Haftungsregelungen nachverhandeln")
    
    elif contract_type == "IT_SERVICE":
        if not analysis.get("sla_vorhanden"):
            empfehlungen.append("Service Level Agreements (SLA) definieren lassen")
        if not analysis.get("datenschutz_erwähnt"):
            empfehlungen.append("Datenschutz-Klauseln ergänzen (DSGVO/DSG)")
    
    elif contract_type == "MIETVERTRAG":
        empfehlungen.append("Wohnungsübergabeprotokoll bei Einzug erstellen")
        if analysis.get("indexierung"):
            empfehlungen.append("Indexierung prüfen und ggf. begrenzen lassen")
    
    elif contract_type == "ARBEITSVERTRAG":
        empfehlungen.append("Vertrag von Fachanwalt prüfen lassen")
        if analysis.get("konkurrenzverbot"):
            empfehlungen.append("Konkurrenzverbot zeitlich/geografisch begrenzen lassen")
    
    empfehlungen.append("Hinweis: Diese Analyse ersetzt keine Rechtsberatung")
    
    return empfehlungen


def generate_email(analysis: dict, contract_type: str, risks: list) -> str:
    """Generiert E-Mail-Vorlage für Rückfragen"""
    
    type_labels = {
        "IT_SERVICE": "IT-Service-Vertrag",
        "HANDWERK": "Handwerksvertrag",
        "MIETVERTRAG": "Mietvertrag",
        "ARBEITSVERTRAG": "Arbeitsvertrag",
        "KAUFVERTRAG": "Kaufvertrag",
        "DIENSTLEISTUNG": "Dienstleistungsvertrag",
        "SONSTIGES": "Vertrag"
    }
    
    contract_label = type_labels.get(contract_type, "Vertrag")
    
    mail = f"""Sehr geehrte Damen und Herren,

vielen Dank für Ihr Vertragsangebot bezüglich {contract_label}.

Nach Prüfung des Vertrags haben wir folgende Rückfragen:

"""
    
    for i, risk in enumerate(risks[:4], 1):  # Max 4 Punkte in E-Mail
        mail += f"{i}. {risk}\n   Können wir hier eine Anpassung vereinbaren?\n\n"
    
    mail += """Wir würden uns freuen, diese Punkte gemeinsam zu klären, um eine für beide Seiten faire Vereinbarung zu treffen.

Für ein kurzes Telefonat oder Meeting stehen wir gerne zur Verfügung.

Mit freundlichen Grüßen"""
    
    return mail


def get_type_label(contract_type: str) -> str:
    """Gibt deutschen Label für Vertragstyp zurück"""
    
    labels = {
        "IT_SERVICE": "IT-Service / Wartung",
        "HANDWERK": "Handwerk / Bau",
        "MIETVERTRAG": "Mietvertrag",
        "ARBEITSVERTRAG": "Arbeitsvertrag",
        "KAUFVERTRAG": "Kaufvertrag",
        "DIENSTLEISTUNG": "Dienstleistung",
        "SONSTIGES": "Allgemeiner Vertrag"
    }
    
    return labels.get(contract_type, "Unbekannt")

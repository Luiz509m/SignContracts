from fastapi import FastAPI, UploadFile, File, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from app.pdf_reader import extract_text_from_pdf
from app.ai_analyzer import analyze_contract
from app.decision_engine import build_decision_output
from app import auth

app = FastAPI(title="SignContracts API")

# CORS aktivieren - ermöglicht Frontend-Zugriff
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In Produktion spezifischer machen
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Models für Requests
class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

# Helper function - aktuellen User aus Token holen
def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Nicht authentifiziert")
    
    try:
        token = authorization.split(" ")[1]
    except IndexError:
        raise HTTPException(status_code=401, detail="Ungültiges Token-Format")
    
    user = auth.verify_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Token ungültig oder abgelaufen")
    
    return user

# ==================== PUBLIC ROUTES ====================

@app.get("/")
def read_root():
    """Health check endpoint"""
    return {"status": "SignContracts Backend läuft"}

@app.post("/auth/register")
def register(request: RegisterRequest):
    """Neuen User registrieren"""
    try:
        user = auth.create_user(request.name, request.email, request.password)
        return {"message": "Registrierung erfolgreich", "user": user}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/auth/login")
def login(request: LoginRequest):
    """User einloggen"""
    user = auth.verify_user(request.email, request.password)
    if not user:
        raise HTTPException(status_code=401, detail="E-Mail oder Passwort falsch")
    
    token = auth.create_session(user["id"])
    return {
        "message": "Login erfolgreich",
        "token": token,
        "user": user
    }

@app.post("/auth/logout")
def logout(authorization: Optional[str] = Header(None)):
    """User ausloggen"""
    if authorization:
        try:
            token = authorization.split(" ")[1]
            auth.delete_session(token)
        except:
            pass
    return {"message": "Logout erfolgreich"}

# ==================== PROTECTED ROUTES ====================

@app.post("/analyze")
async def analyze_contract_endpoint(
    file: UploadFile = File(...),
    authorization: Optional[str] = Header(None)
):
    """
    Analysiert einen hochgeladenen Vertrag
    Benötigt Authentifizierung
    """
    # Authentifizierung prüfen
    user = get_current_user(authorization)
    
    print(f"📄 Analyse gestartet von User: {user['name']}")
    
    try:
        # 1. PDF-Text extrahieren
        text = extract_text_from_pdf(file)
        print(f"✅ PDF extrahiert, Länge: {len(text)} Zeichen")
        
        # 2. KI-Analyse durchführen
        analysis = analyze_contract(text)
        print(f"✅ KI-Analyse fertig")
        
        # 3. Entscheidungs-Output generieren
        decision = build_decision_output(analysis)
        print(f"✅ Decision Engine fertig - Ampel: {decision['ampel']}")
        
        return decision
    
    except Exception as e:
        print(f"❌ Fehler bei Analyse: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analyse fehlgeschlagen: {str(e)}")

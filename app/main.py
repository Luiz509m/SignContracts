import logging
logging.basicConfig(level=logging.DEBUG)
from fastapi import FastAPI, UploadFile, File, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from app.pdf_reader import extract_text_from_pdf
from app.ai_analyzer import analyze_contract
from app.decision_engine import build_decision_output
from app import auth

app = FastAPI()

# CORS aktivieren
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Models for Auth
class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

# Helper function to get current user from token
def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Nicht authentifiziert")
    
    # Extract token from "Bearer <token>"
    try:
        token = authorization.split(" ")[1]
    except IndexError:
        raise HTTPException(status_code=401, detail="Ungültiges Token-Format")
    
    user = auth.verify_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Token ungültig oder abgelaufen")
    
    return user

# Public Routes
@app.get("/")
def read_root():
    return {"status": "SignContracts Backend läuft"}

@app.post("/auth/register")
def register(request: RegisterRequest):
    try:
        user = auth.create_user(request.name, request.email, request.password)
        return {"message": "Registrierung erfolgreich", "user": user}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/auth/login")
def login(request: LoginRequest):
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
    if authorization:
        try:
            token = authorization.split(" ")[1]
            auth.delete_session(token)
        except:
            pass
    return {"message": "Logout erfolgreich"}

# Protected Routes
@app.post("/upload")
async def upload_contract(
    file: UploadFile = File(...),
    authorization: Optional[str] = Header(None)
):
    user = get_current_user(authorization)
    text = extract_text_from_pdf(file)
    return {
        "filename": file.filename,
        "text_preview": text[:1000],
        "user": user["name"]
    }

@app.post("/analyze")
async def analyze_contract_endpoint(
    file: UploadFile = File(...),
    authorization: Optional[str] = Header(None)
):
    user = get_current_user(authorization)
    
    print(f"▶️ Analyse gestartet von User: {user['name']}")

    text = extract_text_from_pdf(file)
    print("▶️ PDF extrahiert, Länge:", len(text))

    text = text[:8000]  # HARD LIMIT
    print("▶️ Text gekürzt")

    analysis = analyze_contract(text)
    print("▶️ KI-Analyse fertig:", analysis)

    decision = build_decision_output(analysis)
    print("▶️ Decision Engine fertig")

    return decision

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.ai_analyzer import analyze_contract
from app.auth import (
    users_db,
    hash_password,
    verify_password,
    create_access_token,
)

app = FastAPI()

# ========================
# CORS – MUSS HIER STEHEN
# ========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "https://luiz509m.github.io",   # <- dein GitHub Pages
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========================
# Health Check (Render!)
# ========================
@app.get("/")
def health():
    return {"status": "SignContracts Backend läuft"}

# ========================
# ANALYSE (noch OHNE Login)
# ========================
@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    try:
        content = await file.read()
        text = content.decode(errors="ignore")

        result = analyze_contract(text)
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ========================
# REGISTRIEREN
# ========================
@app.post("/register")
def register(email: str, password: str):
    if email in users_db:
        raise HTTPException(status_code=400, detail="User existiert bereits")

    users_db[email] = {
        "email": email,
        "password": hash_password(password),
    }
    return {"message": "Registrierung erfolgreich"}

# ========================
# LOGIN
# ========================
@app.post("/login")
def login(email: str, password: str):
    user = users_db.get(email)
    if not user or not verify_password(password, user["password"]):
        raise HTTPException(status_code=401, detail="Falsche Login-Daten")

    token = create_access_token({"sub": email})
    return {
        "access_token": token,
        "token_type": "bearer"
    }

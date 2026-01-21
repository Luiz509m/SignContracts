from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# ✅ 1. App erstellen
app = FastAPI()

# ✅ 2. CORS DIREKT danach (einmal, sauber)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://luiz509m.github.io",
        "http://localhost:5500",
        "http://127.0.0.1:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Health-Check
@app.get("/")
def health():
    return {"status": "SignContracts Backend läuft"}

# ✅ Analyse-Endpoint
@app.post("/analyze")
async def analyze_contract(file: UploadFile = File(...)):
    try:
        # Test: prüfen ob Datei ankommt
        _ = await file.read()

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
            },
            "hinweis": "Keine Rechtsberatung"
        }

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

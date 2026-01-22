from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health():
    return {"status": "SignContracts Backend läuft"}

@app.post("/analyze")
async def analyze_contract(file: UploadFile = File(...)):
    await file.read()

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

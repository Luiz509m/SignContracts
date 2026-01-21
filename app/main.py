from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

# ✅ CORS MUSS DIREKT NACH app = FastAPI() KOMMEN
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # MVP: erlaubt GitHub Pages
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health():
    return {"status": "ok"}

@app.post("/analyse")
async def analyse_contract(file: UploadFile = File(...)):
    try:
        # TEST: nur prüfen ob Upload ankommt
        content = await file.read()

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

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

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

app = FastAPI()

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

@app.get("/")
def health():
    return {"status": "SignContracts Backend läuft"}

@app.post("/analyze")
async def analyze_contract(file: UploadFile = File(...)):
    try:
        content = await file.read()

        if not content:
            return JSONResponse(
                status_code=400,
                content={"error": "Leere Datei"}
            )

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

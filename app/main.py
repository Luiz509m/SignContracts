from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

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
    return {"status": "ok"}

@app.post("/analyze")
async def analyse_contract(file: UploadFile = File(...)):
    return {
        "ampel": "gelb",
        "top_risiken": [{"beschreibung": "Keine SLA definiert"}],
        "empfehlungen": ["SLA vertraglich festhalten"],
        "mail": {"text": "Bitte SLA nachreichen."},
        "hinweis": "Keine Rechtsberatung"
    }

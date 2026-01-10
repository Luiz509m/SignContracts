from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import os

from app.decision_engine import analyze_contract
from app.pdf_utils import extract_text_from_pdf

app = FastAPI(title="SignContracts API")

# CORS – erlaubt Zugriff von GitHub Pages / Browser
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # später einschränken
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health_check():
    return {"status": "ok"}

@app.post("/analyze")
async def analyze_contract_endpoint(file: UploadFile = File(...)):
    try:
        # 1. Temporäre PDF-Datei speichern
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            contents = await file.read()
            tmp.write(contents)
            tmp_path = tmp.name

        # 2. Text extrahieren
        contract_text = extract_text_from_pdf(tmp_path)

        # 3. KI-Analyse
        analysis_result = analyze_contract(contract_text)

        # 4. Datei löschen
        os.remove(tmp_path)

        return {
            "success": True,
            "analysis": analysis_result
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


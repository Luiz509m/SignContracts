from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.auth import (
    users_db,
    hash_password,
    verify_password,
    create_access_token,
    get_current_user
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://deinname.github.io"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/register")
def register(email: str, password: str):
    if email in users_db:
        raise HTTPException(status_code=400, detail="User existiert bereits")

    users_db[email] = {
        "email": email,
        "password": hash_password(password)
    }
    return {"message": "Registrierung erfolgreich"}

@app.post("/login")
def login(email: str, password: str):
    user = users_db.get(email)
    if not user or not verify_password(password, user["password"]):
        raise HTTPException(status_code=401, detail="Falsche Login-Daten")

    token = create_access_token({"sub": email})
    return {"access_token": token, "token_type": "bearer"}

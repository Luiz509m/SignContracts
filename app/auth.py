import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional
import json
import os

# Simple file-based database (for development)
# In production, use a real database like PostgreSQL
DB_FILE = "users.json"

def init_db():
    """Initialize the database file if it doesn't exist"""
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, 'w') as f:
            json.dump({"users": [], "tokens": {}}, f)

def load_db():
    """Load database from file"""
    init_db()
    with open(DB_FILE, 'r') as f:
        return json.load(f)

def save_db(data):
    """Save database to file"""
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def hash_password(password: str) -> str:
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def generate_token() -> str:
    """Generate a random token"""
    return secrets.token_urlsafe(32)

def create_user(name: str, email: str, password: str) -> dict:
    """Create a new user"""
    db = load_db()
    
    # Check if user already exists
    for user in db["users"]:
        if user["email"] == email:
            raise ValueError("E-Mail bereits registriert")
    
    # Create new user
    user = {
        "id": len(db["users"]) + 1,
        "name": name,
        "email": email,
        "password": hash_password(password),
        "created_at": datetime.now().isoformat()
    }
    
    db["users"].append(user)
    save_db(db)
    
    # Return user without password
    return {
        "id": user["id"],
        "name": user["name"],
        "email": user["email"]
    }

def verify_user(email: str, password: str) -> Optional[dict]:
    """Verify user credentials"""
    db = load_db()
    hashed_password = hash_password(password)
    
    for user in db["users"]:
        if user["email"] == email and user["password"] == hashed_password:
            return {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"]
            }
    
    return None

def create_session(user_id: int) -> str:
    """Create a new session token"""
    db = load_db()
    token = generate_token()
    
    db["tokens"][token] = {
        "user_id": user_id,
        "created_at": datetime.now().isoformat(),
        "expires_at": (datetime.now() + timedelta(days=7)).isoformat()
    }
    
    save_db(db)
    return token

def verify_token(token: str) -> Optional[dict]:
    """Verify a session token and return user info"""
    db = load_db()
    
    if token not in db["tokens"]:
        return None
    
    session = db["tokens"][token]
    
    # Check if token is expired
    expires_at = datetime.fromisoformat(session["expires_at"])
    if datetime.now() > expires_at:
        del db["tokens"][token]
        save_db(db)
        return None
    
    # Find user
    user_id = session["user_id"]
    for user in db["users"]:
        if user["id"] == user_id:
            return {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"]
            }
    
    return None

def delete_session(token: str):
    """Delete a session token (logout)"""
    db = load_db()
    if token in db["tokens"]:
        del db["tokens"][token]
        save_db(db)

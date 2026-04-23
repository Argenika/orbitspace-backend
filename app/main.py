import os
from sqlalchemy import text
from app.database import engine
import requests
from pydantic import BaseModel
from fastapi import FastAPI
from jose import jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware

SECRET_KEY = "mi_clave_secreta"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://orbitspace-frontend.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.options("/{rest_of_path:path}")
async def preflight_handler(rest_of_path: str):
    return {"message": "OK"}

security = HTTPBearer()


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except Exception:
        raise HTTPException(status_code=401, detail="Token inválido")


@app.get("/")
def root():
    return {"message": "OrbitSpace funcionando"}

# 🔥 SATÉLITES REALES (API)


@app.get("/satellites/active")
def get_active_satellites():
    API_KEY = "2EX4KD-X6WTG8-KXPEQE-5Q3Z"

    url = f"https://api.n2yo.com/rest/v1/satellite/above/41.3851/2.1734/0/70/20?apiKey={API_KEY}"

    response = requests.get(url)
    data = response.json()

    satellites = []

    for sat in data.get("above", []):
        satellites.append({
            "id": sat["satid"],
            "name": sat["satname"],
            "lat": sat["satlat"],
            "lng": sat["satlng"]
        })

    return satellites

# IA


class ChatRequest(BaseModel):
    question: str


OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


@app.post("/ai/chat")
def chat_ai(data: ChatRequest):
    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    body = {
        "model": "openrouter/free",
        "messages": [
            {"role": "user", "content": data.question}
        ]
    }

    response = requests.post(url, headers=headers, json=body)
    result = response.json()

    return {
        "question": data.question,
        "answer": result["choices"][0]["message"]["content"]
    }

# LOGIN


class LoginRequest(BaseModel):
    email: str
    password: str


@app.post("/auth/login")
def login(data: LoginRequest):
    with engine.connect() as connection:
        result = connection.execute(text("""
            SELECT * FROM usuario WHERE email = :email
        """), {"email": data.email})

        user = result.fetchone()

        if not user:
            raise HTTPException(status_code=401, detail="Usuario no existe")

        return {
            "email": user.email,
            "message": "Usuario encontrado (falta validar password)"
        }

# LANZAMIENTOS


@app.get("/launches")
def get_launches():
    url = "https://ll.thespacedevs.com/2.2.0/launch/upcoming/"
    response = requests.get(url)
    data = response.json()

    launches = []

    for launch in data["results"][:5]:
        launches.append({
            "name": launch["name"],
            "date": launch["net"],
            "provider": launch["launch_service_provider"]["name"]
        })

    return launches


# FAVORITOS
favorites = []


class Favorite(BaseModel):
    id: int
    name: str


@app.post("/favorites")
def add_favorite(fav: Favorite):
    favorites.append(fav)
    return {"message": "Añadido a favoritos", "favorites": favorites}


@app.get("/favorites")
def get_favorites(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = verify_token(token)
    return {
        "message": "Token válido",
        "user": payload,
        "favorites": favorites
    }

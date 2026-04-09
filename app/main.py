import requests
from pydantic import BaseModel
from fastapi import FastAPI
from jose import jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


SECRET_KEY = "mi_clave_secreta"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()
security = HTTPBearer()


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token


def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except Exception:
        raise HTTPException(status_code=401, detail="Token inválido")


@app.get("/")
def root():
    return {"message": "OrbitSpace funcionando"}


@app.get("/satellites/active")
def get_active_satellites():
    return [
        {
            "id": 1,
            "name": "ISS",
            "lat": 40.7128,
            "lng": -74.0060
        },
        {
            "id": 2,
            "name": "Hubble",
            "lat": 28.5383,
            "lng": -81.3792
        }
    ]


# Modelo de entrada (lo que recibe la IA)


class ChatRequest(BaseModel):
    question: str


@app.post("/ai/chat")
def chat_ai(data: ChatRequest):
    return {
        "question": data.question,
        "answer": "Esto es una respuesta de prueba de la IA"
    }


class LoginRequest(BaseModel):
    email: str
    password: str


@app.post("/auth/login")
def login(data: LoginRequest):
    token = create_access_token({"sub": data.email})

    return {
        "email": data.email,
        "message": "Login correcto",
        "token": token
    }


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


# lista temporal (simula base de datos)
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

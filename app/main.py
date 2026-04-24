import os
from sqlalchemy import text
from app.database import engine
import requests
from pydantic import BaseModel
from fastapi import FastAPI, Depends, HTTPException, Request
from jose import jwt
from datetime import datetime, timedelta
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from passlib.context import CryptContext

SECRET_KEY = "mi_clave_secreta"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://orbitspace-frontend.onrender.com",
        "https://orbitspace.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.options("/{rest_of_path:path}")
async def preflight_handler(rest_of_path: str):
    return {"message": "OK"}

security = HTTPBearer(auto_error=False)

pwd_context = CryptContext(
    schemes=["bcrypt"],
    bcrypt__truncate_error=False
)


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

# 🔥 SATÉLITES


@app.get("/satellites/active")
def get_active_satellites():
    API_KEY = "2EX4KD-X6WTG8-KXPEQE-5Q3Z"
    url = f"https://api.n2yo.com/rest/v1/satellite/above/41.3851/2.1734/0/70/20?apiKey={API_KEY}"
    response = requests.get(url)
    data = response.json()

    return [
        {
            "id": sat["satid"],
            "name": sat["satname"],
            "lat": sat["satlat"],
            "lng": sat["satlng"]
        }
        for sat in data.get("above", [])
    ]

# 🤖 IA


class ChatRequest(BaseModel):
    question: str


OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


@app.post("/ai/chat")
def chat_ai(data: ChatRequest):
    try:
        if not OPENROUTER_API_KEY:
            raise HTTPException(status_code=500, detail="Falta API KEY")

        url = "https://openrouter.ai/api/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://orbitspace.vercel.app",
            "X-Title": "OrbitSpace"
        }

        body = {
            "model": "openai/gpt-3.5-turbo",  # 🔥 CAMBIO CLAVE
            "messages": [
                {"role": "user", "content": data.question}
            ]
        }

        response = requests.post(url, headers=headers, json=body)

        print("STATUS:", response.status_code)
        print("RESPONSE:", response.text)

        result = response.json()

        if "error" in result:
            return {
                "question": data.question,
                "answer": f"Error IA REAL: {result['error']}"
            }

        answer = result.get("choices", [{}])[0].get(
            "message", {}).get("content")

        if not answer:
            return {
                "question": data.question,
                "answer": f"Respuesta vacía: {result}"
            }

        return {
            "question": data.question,
            "answer": answer
        }

    except Exception as e:
        print("ERROR IA:", str(e))
        return {
            "question": data.question,
            "answer": f"Error IA: {str(e)}"
        }

# 🔐 LOGIN / REGISTER


class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    nombre: str
    email: str
    password: str


@app.post("/auth/login")
def login(data: LoginRequest):
    with engine.connect() as connection:
        user = connection.execute(text("""
            SELECT * FROM usuario WHERE email = :email
        """), {"email": data.email}).fetchone()

        if not user:
            raise HTTPException(status_code=401, detail="Usuario no existe")

        if not pwd_context.verify(data.password, user.password):
            raise HTTPException(status_code=401, detail="Password incorrecto")

        token = create_access_token({"sub": user.user_id})

        return {
            "token": token,
            "user": {
                "nombre": user.nombre,
                "email": user.email,
                "fecha_registro": str(user.fecha_registro),
                "horas_vuelo": user.horas_vuelo,
                "alertas": 0
            }
        }


@app.post("/auth/register")
def register(data: RegisterRequest):
    hashed_password = pwd_context.hash(data.password)

    with engine.begin() as connection:
        existing = connection.execute(text("""
            SELECT * FROM usuario WHERE email = :email
        """), {"email": data.email}).fetchone()

        if existing:
            raise HTTPException(status_code=400, detail="Usuario ya existe")

        result = connection.execute(text("""
            INSERT INTO usuario (nombre, email, password)
            VALUES (:nombre, :email, :password)
        """), {
            "nombre": data.nombre,
            "email": data.email,
            "password": hashed_password
        })

        user_id = result.lastrowid

    token = create_access_token({"sub": user_id})

    return {
        "message": "Usuario creado",
        "token": token
    }

# 🚀 LANZAMIENTOS


@app.get("/launches")
def get_launches():
    with engine.connect() as connection:
        result = connection.execute(text("""
            SELECT 
                m.nombre_mision,
                l.horario_lanza AS fecha_lanzamiento,
                o.siglas as organizacion,
                v.nombre_vehiculo
            FROM mision m
            LEFT JOIN lanzamiento l ON m.lanzamiento_id = l.lanza_id
            LEFT JOIN organizacion o ON m.siglas_org = o.siglas
            LEFT JOIN vehiculo v ON m.vehiculo1_id = v.vehiculo_id
        """))

        return [
            {
                "name": row.nombre_mision,
                "date": str(row.fecha_lanzamiento),
                "organization": row.organizacion,
                "vehicle": row.nombre_vehiculo
            }
            for row in result
        ]

# ❤️ FAVORITOS


@app.get("/favorites")
def get_favorites(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not credentials:
        raise HTTPException(status_code=401)

    payload = verify_token(credentials.credentials)
    user_id = payload.get("sub")

    with engine.connect() as connection:
        result = connection.execute(text("""
            SELECT v.*
            FROM vehiculo v
            INNER JOIN favorito f ON v.vehiculo_id = f.vehiculo_id
            WHERE f.user_id = :user_id
        """), {"user_id": user_id})

        return [dict(row._mapping) for row in result]


@app.post("/favorites/{vehiculo_id}")
def toggle_favorite(vehiculo_id: int, credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not credentials:
        raise HTTPException(status_code=401)

    payload = verify_token(credentials.credentials)
    user_id = payload.get("sub")

    with engine.begin() as connection:
        existing = connection.execute(text("""
            SELECT * FROM favorito
            WHERE user_id = :user_id AND vehiculo_id = :vehiculo_id
        """), {"user_id": user_id, "vehiculo_id": vehiculo_id}).fetchone()

        if existing:
            connection.execute(text("""
                DELETE FROM favorito
                WHERE user_id = :user_id AND vehiculo_id = :vehiculo_id
            """), {"user_id": user_id, "vehiculo_id": vehiculo_id})
            return {"message": "Eliminado"}

        connection.execute(text("""
            INSERT INTO favorito (user_id, vehiculo_id)
            VALUES (:user_id, :vehiculo_id)
        """), {"user_id": user_id, "vehiculo_id": vehiculo_id})

        return {"message": "Añadido"}
